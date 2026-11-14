import unittest

from tools.gfa_token_tables import (
    CHARACTER_CAPACITY,
    TOKEN_CAPACITY,
    Record,
    TableFormatError,
    build_from_records,
    dispatch_vector_target,
    lookup_character_byte,
    lookup_token_word,
    parse_records,
    resolve_text_pointer,
)


class ParseRecordTests(unittest.TestCase):
    def test_character_record_key_and_terminated_extent(self):
        # prefix=0, discriminator=1 adds the extended-character bias 0xE0.
        text = bytes([0, 0, 1, 0x41, 0xFF, 0x99])
        records, extent = parse_records(text, 0, "character_map", 0)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].lookup_key, 0x121)
        self.assertEqual(records[0].relative_pointer, 0)
        self.assertEqual(extent, text[:5])

    def test_token_record_uses_big_endian_byte_offset(self):
        text = bytes([0, 0, 0x01, 0xCC, 0xAA, 0xBB, 0xFF])
        records, _ = parse_records(text, 0, "token_map", 0)
        self.assertEqual(records[0].lookup_key, 0x01CC)
        self.assertEqual(records[0].relative_pointer, 0)

    def test_record_overrun_and_missing_terminator_are_rejected(self):
        with self.assertRaises(TableFormatError):
            parse_records(bytes([3, 0]), 0, "character_map", 0)
        with self.assertRaises(TableFormatError):
            parse_records(bytes([0, 0, 0, 1]), 0, "character_map", 0)


class TableConstructionTests(unittest.TestCase):
    def test_capacity_hole_fill_order_and_68000_word_encoding(self):
        chars = [
            Record(105, 0, b"", 1, 5),
            Record(107, 0, b"", 3, 7),
        ]
        tokens = [Record(120, 0, b"", 2, 20)]
        build = build_from_records(chars, tokens, word_before_character_map=9)

        self.assertEqual(len(build.character_words), CHARACTER_CAPACITY)
        self.assertEqual(len(build.token_words), TOKEN_CAPACITY)
        self.assertEqual(build.character_words[:5], (9, 5, 5, 7, 7))
        # Token slot zero inherits character slot 463; slot one is explicit.
        self.assertEqual(build.token_words[:3], (7, 20, 20))
        self.assertEqual(build.token_words[0x3C], 0)
        self.assertEqual(build.token_words[0x3F], 0)
        self.assertTrue(all(x == 0 for x in build.token_words[0x4C:0x58]))
        self.assertEqual(build.combined_bytes[:4], b"\x00\x09\x00\x05")

    def test_duplicate_key_last_record_wins_and_semantic_mutation_changes_hash(self):
        first = Record(100, 0, b"", 4, 0x10)
        last = Record(102, 0, b"", 4, 0x12)
        token = Record(104, 0, b"", 2, 0x14)
        baseline = build_from_records([first, last], [token])
        changed = build_from_records([first, Record(102, 0, b"", 6, 0x12)], [token])
        self.assertEqual(baseline.character_words[4], 0x12)
        self.assertNotEqual(baseline.combined_bytes, changed.combined_bytes)

    def test_invalid_table_indices_and_odd_token_offsets_are_rejected(self):
        with self.assertRaises(TableFormatError):
            build_from_records([Record(1, 0, b"", CHARACTER_CAPACITY, 2)], [])
        with self.assertRaises(TableFormatError):
            build_from_records([], [Record(1, 0, b"", 1, 2)])
        with self.assertRaises(TableFormatError):
            build_from_records([], [Record(1, 0, b"", TOKEN_CAPACITY * 2, 2)])

    def test_consumer_scaling_and_signed_text_relative_pointer(self):
        build = build_from_records(
            [Record(0x11FCA, 4, b"", 0x41, 0xF310)],
            [Record(0x11132, 0, b"", 0xE6, 0xE478)],
        )
        self.assertEqual(lookup_token_word(build, 0x01CC), 0xE478)
        self.assertEqual(lookup_character_byte(build, 0x41), 0xF310)
        self.assertEqual(resolve_text_pointer(0xE478, 0x20000), 0x11132)
        self.assertEqual(resolve_text_pointer(0xF310, 0x20000), 0x11FCA)
        with self.assertRaises(TableFormatError):
            lookup_token_word(build, 0x01CE)
        with self.assertRaises(TableFormatError):
            lookup_character_byte(build, 0x1D0)

    def test_dispatcher_target_resolution_and_control_flow_mutation(self):
        text = bytearray(0x9000)
        text[0x1BF8:0x1BFC] = bytes.fromhex("0000869a")
        text[0x1BFC:0x1C00] = bytes.fromhex("00008698")
        self.assertEqual(dispatch_vector_target(bytes(text), 0), 0x869A)
        self.assertEqual(dispatch_vector_target(bytes(text), 4), 0x8698)
        text[0x1BF8:0x1BFC] = bytes.fromhex("0000869c")
        self.assertEqual(dispatch_vector_target(bytes(text), 0), 0x869C)
        with self.assertRaises(TableFormatError):
            dispatch_vector_target(bytes(text), 2)
        with self.assertRaises(TableFormatError):
            dispatch_vector_target(bytes(text), 26 * 4)


if __name__ == "__main__":
    unittest.main()
