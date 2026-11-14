#!/usr/bin/env python3
"""Extract one file from an Atari ST FAT12 floppy image (raw .ST)."""
from __future__ import annotations

import argparse
from pathlib import Path


class Fat12Image:
    def __init__(self, image: bytes):
        if len(image) < 512:
            raise ValueError("image is shorter than one boot sector")
        self.image = image
        b = image[:512]
        self.bytes_per_sector = int.from_bytes(b[11:13], "little")
        self.sectors_per_cluster = b[13]
        self.reserved = int.from_bytes(b[14:16], "little")
        self.fat_count = b[16]
        self.root_entries = int.from_bytes(b[17:19], "little")
        self.sectors_per_fat = int.from_bytes(b[22:24], "little")
        if self.bytes_per_sector != 512 or not self.sectors_per_cluster or not self.fat_count or not self.sectors_per_fat:
            raise ValueError("unsupported Atari FAT12 BPB")
        self.root_sectors = (self.root_entries * 32 + 511) // 512
        self.root_sector = self.reserved + self.fat_count * self.sectors_per_fat
        self.data_sector = self.root_sector + self.root_sectors
        fat_end = (self.reserved + self.sectors_per_fat) * 512
        self.fat = image[self.reserved * 512:fat_end]
        if len(self.fat) != self.sectors_per_fat * 512:
            raise ValueError("truncated FAT")

    def next_cluster(self, cluster: int) -> int:
        pos = cluster + cluster // 2
        if pos + 1 >= len(self.fat):
            raise ValueError(f"cluster {cluster} is outside the FAT")
        pair = self.fat[pos] | (self.fat[pos + 1] << 8)
        return ((pair >> 4) if cluster & 1 else pair) & 0xFFF

    def chain(self, first: int) -> list[int]:
        result, seen, cluster = [], set(), first
        while 2 <= cluster < 0xFF8:
            if cluster in seen:
                raise ValueError("FAT cluster loop")
            seen.add(cluster); result.append(cluster)
            cluster = self.next_cluster(cluster)
        if cluster < 0xFF8 and cluster != 0xFF7:
            raise ValueError(f"invalid FAT chain terminator 0x{cluster:03X}")
        return result

    def cluster_bytes(self, cluster: int) -> bytes:
        sector = self.data_sector + (cluster - 2) * self.sectors_per_cluster
        start = sector * self.bytes_per_sector
        size = self.sectors_per_cluster * self.bytes_per_sector
        data = self.image[start:start + size]
        if len(data) != size:
            raise ValueError(f"cluster {cluster} points past end of image")
        return data

    @staticmethod
    def short_name(entry: bytes) -> str:
        stem = entry[:8].decode("ascii", "replace").rstrip()
        ext = entry[8:11].decode("ascii", "replace").rstrip()
        return stem + ("." + ext if ext else "")

    def directory_entries(self, directory_cluster: int | None):
        if directory_cluster is None:
            start = self.root_sector * 512
            raw = self.image[start:start + self.root_entries * 32]
        else:
            raw = b"".join(self.cluster_bytes(c) for c in self.chain(directory_cluster))
        for offset in range(0, len(raw) - 31, 32):
            entry = raw[offset:offset + 32]
            if entry[0] == 0:
                break
            if entry[0] == 0xE5 or entry[11] in (0x0F, 0x08):
                continue
            yield entry

    def extract(self, member: str, recover_gemdos: bool = False) -> bytes:
        parts = [x for x in member.replace("\\", "/").split("/") if x and x != "."]
        if not parts or any(x == ".." for x in parts):
            raise ValueError("member must be a non-empty path inside the image")
        directory = None
        selected = None
        for index, part in enumerate(parts):
            selected = next((e for e in self.directory_entries(directory)
                             if self.short_name(e).casefold() == part.casefold()), None)
            if selected is None:
                raise FileNotFoundError(f"member not found: {member}")
            if index < len(parts) - 1:
                if not selected[11] & 0x10:
                    raise NotADirectoryError("path component is not a directory: " + part)
                directory = int.from_bytes(selected[26:28], "little")
        assert selected is not None
        if selected[11] & 0x10:
            raise IsADirectoryError(member)
        size = int.from_bytes(selected[28:32], "little")
        first = int.from_bytes(selected[26:28], "little")
        reachable = b"".join(self.cluster_bytes(c) for c in self.chain(first))
        if len(reachable) < size:
            if not recover_gemdos:
                raise ValueError(f"truncated member: expected {size}, got {len(reachable)} bytes")
            content, _ = recover_gemdos_prg(reachable)
            if len(content) > len(reachable):
                raise ValueError("GEMDOS executable extent exceeds reachable FAT chain")
            return content
        content = reachable[:size]
        return content


def recover_gemdos_prg(reachable: bytes) -> tuple[bytes, int]:
    """Trim a short FAT chain to a complete GEMDOS PRG header/relocation end.

    This is an explicit recovery path for inconsistent directory size fields;
    it never invents missing bytes and requires a complete PRG section layout
    and a terminated relocation table.
    """
    if len(reachable) < 32 or reachable[:2] != b"\x60\x1a":
        raise ValueError("short chain is not a complete GEMDOS PRG candidate")
    text, data, _bss, symbols = (int.from_bytes(reachable[i:i + 4], "big")
                                 for i in (2, 6, 10, 14))
    pos = 28 + text + data + symbols
    if pos + 4 > len(reachable):
        raise ValueError("GEMDOS sections extend beyond reachable FAT chain")
    current = int.from_bytes(reachable[pos:pos + 4], "big")
    pos += 4
    relocations = 0
    if current:
        relocations = 1
        while pos < len(reachable):
            delta = reachable[pos]
            pos += 1
            if delta == 0:
                return reachable[:pos], relocations
            if delta == 1:
                current += 254
            else:
                current += delta
                relocations += 1
        raise ValueError("unterminated GEMDOS relocation table")
    return reachable[:pos], relocations


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("member", help="path, e.g. COMPILER/GFA_BCOM.PRG")
    parser.add_argument("output", type=Path)
    parser.add_argument("--recover-gemdos", action="store_true",
                         help="recover a complete PRG from a FAT chain shorter than its directory size")
    args = parser.parse_args(argv)
    data = Fat12Image(args.image.read_bytes()).extract(args.member, recover_gemdos=args.recover_gemdos)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    print(f"extracted {args.member}: {len(data)} bytes -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
