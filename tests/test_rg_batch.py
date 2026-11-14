from __future__ import annotations
import contextlib
import io
from pathlib import Path
import stat
import tempfile
import unittest

from tools.rg_batch import main, parse_args, sha256, validate

class RgBatchTests(unittest.TestCase):
    def test_rejects_6502(self):
        args = parse_args(["--target", "tbxl-1.5", "--role", "interpreter", "--input", "missing.xex"])
        with self.assertRaisesRegex(ValueError, "6502"):
            validate(args)

    def test_rejects_disk_image(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "disk.st"
            path.write_bytes(b"012345")
            args = parse_args(["--target", "gfa-2.02", "--role", "interpreter", "--input", str(path)])
            with self.assertRaisesRegex(ValueError, "disk image"):
                validate(args)

    def test_rejects_bad_magic(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "FALSE.PRG"
            path.write_bytes(b"NOPE")
            args = parse_args(["--target", "gfa-1.0", "--role", "interpreter", "--input", str(path)])
            with self.assertRaisesRegex(ValueError, "magic"):
                validate(args)

    def test_dry_run_v2_vs_v1(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            program = base / "SAMPLE.PRG"
            program.write_bytes(b"\x60\x1a" + b"\0" * 26 + b"\x4e\x75")
            tool = base / "rg-dis"
            tool.write_text("#!/bin/sh\nif [ \"$1\" = '--version' ]; then echo 'rg-dis 0.11.46'; fi\n")
            tool.chmod(tool.stat().st_mode | stat.S_IXUSR)
            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = main(["--target", "gfa-2.02", "--role", "interpreter", "--input", str(program),
                           "--rg", str(tool), "--dry-run"])
            self.assertEqual(rc, 0)
            self.assertIn("--annotate-gfa", stdout.getvalue())
            self.assertIn("--no-annotate-gfa", stdout.getvalue())
            self.assertEqual(len(sha256(program)), 64)
            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = main(["--target", "gfa-1.0", "--role", "interpreter", "--input", str(program),
                           "--rg", str(tool), "--dry-run"])
            self.assertEqual(rc, 0)
            self.assertNotIn("--annotate-gfa", stdout.getvalue())

if __name__ == "__main__":
    unittest.main()
