#!/usr/bin/env python3
"""Inspect and reproduce the GFA 3.6 startup lookup-table builder.

Offsets and record layouts are TEXT-relative, as established from the 68000
instructions at TEXT:$1569E. No historical table bytes are emitted by this
module; the CLI reports measurements and SHA-256 fingerprints only.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
from pathlib import Path
import struct
from typing import Iterable


TEXT_OFFSETS = {
    "character_map": 0x11EDB,
    "token_map": 0x1111E,
    "string_base": 0x12CBA,
}
CHARACTER_CAPACITY = 0x1D0  # 464 words, indices 0..463
TOKEN_CAPACITY = 0x200      # 512 words, byte indices 0..1022
TABLE_WORDS = CHARACTER_CAPACITY + TOKEN_CAPACITY


class TableFormatError(ValueError):
    """The PRG or a static table does not match the observed layout."""


@dataclass(frozen=True)
class Record:
    text_offset: int
    prefix_length: int
    raw: bytes
    lookup_key: int
    relative_pointer: int


@dataclass(frozen=True)
class TableBuild:
    character_words: tuple[int, ...]
    token_words: tuple[int, ...]
    character_records: tuple[Record, ...]
    token_records: tuple[Record, ...]
    character_map_bytes: bytes
    token_map_bytes: bytes
    boundary_word_before_character_map: int

    @property
    def combined_words(self) -> tuple[int, ...]:
        return self.character_words + self.token_words

    @property
    def combined_bytes(self) -> bytes:
        return b"".join(struct.pack(">H", word) for word in self.combined_words)


def extract_text(prg: bytes) -> bytes:
    """Return a validated TOS PRG TEXT section (28-byte GEMDOS header)."""
    if len(prg) < 28:
        raise TableFormatError("truncated GEMDOS PRG header")
    magic, text_size, data_size, bss_size, symbol_size, reserved, flags, absflag = struct.unpack(
        ">HIIIIIIH", prg[:28]
    )
    if magic != 0x601A:
        raise TableFormatError(f"unexpected PRG magic 0x{magic:04X}")
    end = 28 + text_size + data_size + symbol_size
    if end > len(prg):
        raise TableFormatError("PRG sections exceed file size")
    # Keep these fields parsed and sanity-checked without interpreting them.
    if bss_size < 0 or reserved < 0 or flags < 0 or absflag not in (0, 1):
        raise TableFormatError("invalid GEMDOS PRG header fields")
    return prg[28:28 + text_size]


def parse_records(text: bytes, start: int, kind: str, string_base: int) -> tuple[tuple[Record, ...], bytes]:
    """Parse length-prefixed records until the observed negative-byte marker.

    Character-map records advance by 4 + prefix_length. Their lookup key is
    byte[prefix_length+3], plus 0xE0 when byte[prefix_length+2] is nonzero.
    Token-map records advance by 6 + prefix_length. Their key is the big-endian
    word at prefix_length+2. In both cases the stored value is the low 16 bits
    of (record TEXT offset - TEXT:$12CBA).
    """
    if kind == "character_map":
        base_size = 4
    elif kind == "token_map":
        base_size = 6
    else:
        raise ValueError(f"unknown table kind: {kind}")
    if start < 0 or start >= len(text):
        raise TableFormatError(f"{kind}: start outside TEXT")

    pos = start
    records: list[Record] = []
    while pos < len(text):
        prefix = text[pos]
        if prefix & 0x80:
            end = pos + 1
            return tuple(records), text[start:end]
        size = base_size + prefix
        end = pos + size
        if end > len(text):
            raise TableFormatError(f"{kind}: record at 0x{pos:X} overruns TEXT")
        raw = text[pos:end]
        if kind == "character_map":
            discriminator = raw[prefix + 2]
            byte_key = raw[prefix + 3]
            lookup_key = byte_key + (0xE0 if discriminator else 0)
        else:
            lookup_key = (raw[prefix + 2] << 8) | raw[prefix + 3]
        relative_pointer = (pos - string_base) & 0xFFFF
        records.append(Record(pos, prefix, raw, lookup_key, relative_pointer))
        pos = end
    raise TableFormatError(f"{kind}: missing high-bit record terminator")


def _write_word(words: list[int], slot: int, value: int, label: str) -> None:
    if not 0 <= slot < len(words):
        raise TableFormatError(f"{label}: lookup slot {slot} outside table of {len(words)} words")
    words[slot] = value & 0xFFFF


def _fill_zero_slots(words: list[int], preceding_word: int) -> None:
    """Mirror MOVE.W -4(A0),-2(A0) after post-incrementing A0.

    A zero word inherits the preceding word. Slot zero reads the word just
    before the table; callers supply that out-of-table dependency explicitly.
    """
    previous = preceding_word & 0xFFFF
    for index, value in enumerate(words):
        if value == 0:
            words[index] = previous
        else:
            previous = value


def build_from_records(character_records: Iterable[Record], token_records: Iterable[Record],
                       character_map_bytes: bytes = b"", token_map_bytes: bytes = b"", *,
                       word_before_character_map: int = 0) -> TableBuild:
    character_records = tuple(character_records)
    token_records = tuple(token_records)
    character_words = [0] * CHARACTER_CAPACITY
    token_words = [0] * TOKEN_CAPACITY

    for record in character_records:
        _write_word(character_words, record.lookup_key, record.relative_pointer, "character map")
    for record in token_records:
        if record.lookup_key & 1:
            raise TableFormatError(f"token map byte offset 0x{record.lookup_key:X} is odd")
        _write_word(token_words, record.lookup_key // 2, record.relative_pointer, "token map")

    _fill_zero_slots(character_words, word_before_character_map)
    # The two arrays are contiguous. The token-map fill at slot zero reads the
    # last word of the character map (workspace+$10CA), not cleared memory.
    _fill_zero_slots(token_words, character_words[-1])

    # TEXT:$1573A..$1574A explicitly blank three token-table subranges.
    for slot in (0x7E // 2, 0x78 // 2, *range(0x98 // 2, 0xB0 // 2)):
        token_words[slot] = 0

    return TableBuild(
        tuple(character_words), tuple(token_words), character_records,
        token_records, character_map_bytes, token_map_bytes,
        word_before_character_map & 0xFFFF,
    )


def build_from_prg(prg: bytes) -> TableBuild:
    text = extract_text(prg)
    char_records, char_bytes = parse_records(
        text, TEXT_OFFSETS["character_map"], "character_map", TEXT_OFFSETS["string_base"]
    )
    token_records, token_bytes = parse_records(
        text, TEXT_OFFSETS["token_map"], "token_map", TEXT_OFFSETS["string_base"]
    )
    return build_from_records(char_records, token_records, char_bytes, token_bytes)


def lookup_token_word(build: TableBuild, token_word: int) -> int:
    """Mirror LSR.W #1 then MOVE.W (A3,D0.W): token_word>>2 is slot index."""
    if not 0 <= token_word <= 0xFFFF or token_word & 0x03:
        raise TableFormatError(f"token word 0x{token_word:X} is not a word-table key")
    slot = token_word >> 2
    if slot >= TOKEN_CAPACITY:
        raise TableFormatError(f"token word 0x{token_word:X} is outside token table")
    return build.token_words[slot]


def lookup_character_byte(build: TableBuild, character_byte: int) -> int:
    """Mirror ADD.W D0,D0 followed by word-indexed access at A6+$D2C."""
    if not 0 <= character_byte < CHARACTER_CAPACITY:
        raise TableFormatError(f"character byte 0x{character_byte:X} is outside character table")
    return build.character_words[character_byte]


def resolve_text_pointer(relative_pointer: int, text_size: int) -> int:
    """Resolve a stored word using 68000 sign extension in ADDA.W."""
    if not 0 <= relative_pointer <= 0xFFFF:
        raise TableFormatError("relative pointer is not a 16-bit word")
    signed = relative_pointer if relative_pointer < 0x8000 else relative_pointer - 0x10000
    result = TEXT_OFFSETS["string_base"] + signed
    if not 0 <= result < text_size:
        raise TableFormatError(f"resolved TEXT offset 0x{result:X} outside TEXT")
    return result


def dispatch_vector_target(text: bytes, d6_byte_offset: int) -> int:
    """Resolve one first-level static vector entry; handler code stays opaque."""
    vector_start = 0x1BF8
    vector_entries = 26
    if d6_byte_offset < 0 or d6_byte_offset % 4 or d6_byte_offset >= vector_entries * 4:
        raise TableFormatError(f"dispatcher D6 byte offset 0x{d6_byte_offset:X} is invalid")
    entry = vector_start + d6_byte_offset
    if entry + 4 > len(text):
        raise TableFormatError("dispatcher vector entry exceeds TEXT")
    target = struct.unpack(">I", text[entry:entry + 4])[0]
    if target >= len(text):
        raise TableFormatError(f"dispatcher target 0x{target:X} is outside TEXT")
    return target


def table_report(build: TableBuild, prg: bytes) -> dict:
    text = extract_text(prg)
    char_written = [record.lookup_key for record in build.character_records]
    token_written = [record.lookup_key for record in build.token_records]
    char_unique = len(set(char_written))
    token_unique = len(set(token_written))
    return {
        "prg_bytes": len(prg),
        "prg_sha256": hashlib.sha256(prg).hexdigest(),
        "text_bytes": len(text),
        "text_sha256": hashlib.sha256(text).hexdigest(),
        "table_workspace": {
            "character_base": 0xD2C,
            "character_capacity_words": CHARACTER_CAPACITY,
            "character_key_slots_observed": [min(char_written), max(char_written)],
            "token_base": 0x10CC,
            "token_capacity_words": TOKEN_CAPACITY,
            "token_key_byte_offsets_observed": [min(token_written), max(token_written)],
            "combined_base": 0xD2C,
            "combined_words": TABLE_WORDS,
            "combined_bytes": TABLE_WORDS * 2,
            "contiguous": 0x10CC == 0xD2C + CHARACTER_CAPACITY * 2,
            "word_before_character_table_workspace_offset": 0xD2A,
            "first_token_fill_source_workspace_offset": 0x10CA,
        },
        "character_map": {
            "text_start": TEXT_OFFSETS["character_map"],
            "text_end_inclusive": TEXT_OFFSETS["character_map"] + len(build.character_map_bytes) - 1,
            "source_bytes_including_terminator": len(build.character_map_bytes),
            "record_count": len(build.character_records),
            "unique_keys": char_unique,
            "duplicate_key_records": len(char_written) - char_unique,
            "max_prefix_length": max(r.prefix_length for r in build.character_records),
            "sha256_with_terminator": hashlib.sha256(build.character_map_bytes).hexdigest(),
        },
        "token_map": {
            "text_start": TEXT_OFFSETS["token_map"],
            "text_end_inclusive": TEXT_OFFSETS["token_map"] + len(build.token_map_bytes) - 1,
            "source_bytes_including_terminator": len(build.token_map_bytes),
            "record_count": len(build.token_records),
            "unique_keys": token_unique,
            "duplicate_key_records": len(token_written) - token_unique,
            "max_prefix_length": max(r.prefix_length for r in build.token_records),
            "sha256_with_terminator": hashlib.sha256(build.token_map_bytes).hexdigest(),
        },
        "generated": {
            "character_table_sha256_be_words": hashlib.sha256(
                b"".join(struct.pack(">H", x) for x in build.character_words)
            ).hexdigest(),
            "token_table_sha256_be_words": hashlib.sha256(
                b"".join(struct.pack(">H", x) for x in build.token_words)
            ).hexdigest(),
            "combined_sha256_be_words": hashlib.sha256(build.combined_bytes).hexdigest(),
            "initial_word_before_character_map": build.boundary_word_before_character_map,
            "manual_zero_token_slots": [0x3C, 0x3F, *range(0x4C, 0x58)],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prg", type=Path)
    parser.add_argument("--json", action="store_true", help="emit structured report")
    args = parser.parse_args(argv)
    import json
    prg = args.prg.read_bytes()
    report = table_report(build_from_prg(prg), prg)
    print(json.dumps(report, indent=2) if args.json else _format_report(report))
    return 0


def _format_report(report: dict) -> str:
    table = report["table_workspace"]
    generated = report["generated"]
    return "\n".join([
        f"TEXT bytes: {report['text_bytes']}",
        f"character map: {report['character_map']['record_count']} records, "
        f"{report['character_map']['unique_keys']} unique keys, "
        f"SHA-256 {report['character_map']['sha256_with_terminator']}",
        f"token map: {report['token_map']['record_count']} records, "
        f"{report['token_map']['unique_keys']} unique keys, "
        f"SHA-256 {report['token_map']['sha256_with_terminator']}",
        f"workspace tables: {table['combined_words']} words / {table['combined_bytes']} bytes; "
        f"contiguous={table['contiguous']}",
        f"generated BE-word tables SHA-256: {generated['combined_sha256_be_words']}",
    ])


if __name__ == "__main__":
    raise SystemExit(main())
