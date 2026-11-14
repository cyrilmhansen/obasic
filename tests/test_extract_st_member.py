import unittest

from tools.extract_st_member import recover_gemdos_prg


def prg(text: bytes, reloc: bytes, padding: bytes = b"") -> bytes:
    header = bytearray(28)
    header[:2] = b"\x60\x1a"
    header[2:6] = len(text).to_bytes(4, "big")
    return bytes(header) + text + reloc + padding


class GemdosRecoveryTests(unittest.TestCase):
    def test_trims_padding_after_terminated_relocation_table(self):
        raw = prg(b"\x4e\x71\x4e\x75", (6).to_bytes(4, "big") + b"\x02\x01\x00", b"padding")
        recovered, relocation_count = recover_gemdos_prg(raw)
        self.assertEqual(len(recovered), 28 + 4 + 7)
        self.assertEqual(relocation_count, 2)

    def test_zero_relocation_marker_ends_file(self):
        raw = prg(b"\x4e\x75", b"\0\0\0\0", b"tail")
        recovered, relocation_count = recover_gemdos_prg(raw)
        self.assertEqual(len(recovered), 28 + 2 + 4)
        self.assertEqual(relocation_count, 0)

    def test_rejects_unterminated_relocations(self):
        raw = prg(b"\x4e\x71", (6).to_bytes(4, "big") + b"\x02\x03\x04")
        with self.assertRaisesRegex(ValueError, "unterminated"):
            recover_gemdos_prg(raw)


if __name__ == "__main__":
    unittest.main()
