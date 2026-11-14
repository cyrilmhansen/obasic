from __future__ import annotations
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from tools.acquire import AcquisitionError, main, output_filename, registry, sha256


class AcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.catalog = self.root / "sources.json"
        self.store = self.root / "work"
        self.sample = self.root / "original.st"
        self.sample.write_bytes(b"ST disk\0\x11\x22")
        self.art = {"id": "gfa-2.02-disk", "target": "gfa-2.02", "role": "distribution",
                    "description": "disk", "catalog_url": "https://example.org/catalog", "url": None, "sha256": None}
        self.catalog.write_text(json.dumps({"schema": 1, "artifacts": [self.art]}))

    def run_cli(self, *params):
        with contextlib.redirect_stdout(io.StringIO()) as stdout, contextlib.redirect_stderr(io.StringIO()) as stderr:
            rc = main(["--registry", str(self.catalog), "--store", str(self.store), *params])
        return rc, stdout.getvalue(), stderr.getvalue()

    def test_import_then_pin_verify_and_receipt(self):
        rc, out, err = self.run_cli("import", "gfa-2.02-disk", "--file", str(self.sample))
        self.assertEqual(rc, 2)
        self.assertIn("--allow-unpinned", err)
        rc, out, err = self.run_cli("import", "gfa-2.02-disk", "--file", str(self.sample), "--allow-unpinned")
        self.assertEqual((rc, err), (0, ""))
        path = self.store / "gfa-2.02-disk" / "original.st"
        self.assertEqual(path.read_bytes(), self.sample.read_bytes())
        receipt = json.loads(Path(str(path) + ".receipt.json").read_text())
        self.assertFalse(receipt["pinned"])
        self.assertEqual(receipt["sha256"], sha256(self.sample))
        rc, out, err = self.run_cli("pin", "gfa-2.02-disk", "--file", str(path))
        self.assertEqual(rc, 0)
        rc, out, err = self.run_cli("verify", "gfa-2.02-disk", "--file", str(path))
        self.assertEqual(rc, 0)
        self.assertIn("VERIFIED", out)

    def test_pin_mismatch_is_rejected(self):
        self.art["sha256"] = "0" * 64
        self.catalog.write_text(json.dumps({"schema": 1, "artifacts": [self.art]}))
        rc, out, err = self.run_cli("import", "gfa-2.02-disk", "--file", str(self.sample))
        self.assertEqual(rc, 2)
        self.assertIn("mismatch", err)
        self.assertFalse((self.store / "gfa-2.02-disk" / "original.st").exists())

    def test_download_requires_direct_url_and_https(self):
        rc, out, err = self.run_cli("fetch", "gfa-2.02-disk", "--allow-unpinned")
        self.assertEqual(rc, 2)
        self.assertIn("no direct download URL", err)
        rc, out, err = self.run_cli("fetch", "gfa-2.02-disk", "--url", "http://example.org/file.st", "--allow-unpinned")
        self.assertEqual(rc, 2)
        self.assertIn("HTTPS", err)

    def test_filename_sanitization(self):
        self.assertEqual(output_filename(None, "https://example.org/disks/foo%20bar.zip"), "foo bar.zip")
        with self.assertRaises(AcquisitionError):
            output_filename("../escape.st", None)

    def test_registry_validation(self):
        self.art["id"] = "../escape"
        self.catalog.write_text(json.dumps({"schema": 1, "artifacts": [self.art]}))
        with self.assertRaises(AcquisitionError):
            registry(self.catalog)


if __name__ == "__main__":
    unittest.main()
