#!/usr/bin/env python3
"""Fetch/import historical archives with provenance receipts, outside Git."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "artifacts" / "sources.json"
STORE = ROOT / "work" / "originals"
MAX_BYTES = 100 * 1024 * 1024
DIGEST = re.compile(r"^[0-9a-f]{64}$")
SAFE_NAME = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.+() -]{0,180}$")


class AcquisitionError(Exception):
    pass


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as file:
        for buf in iter(lambda: file.read(1024 * 1024), b""):
            h.update(buf)
    return h.hexdigest()


def registry(path: Path):
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("schema") != 1 or not isinstance(obj.get("artifacts"), list):
        raise AcquisitionError("Registry schema 1 and artifacts array are required")
    found = {}
    for a in obj["artifacts"]:
        ident = a.get("id")
        if not isinstance(ident, str) or not re.fullmatch(r"[a-z0-9][a-z0-9.-]*", ident):
            raise AcquisitionError(f"Unsafe artifact ID: {ident!r}")
        if ident in found:
            raise AcquisitionError(f"Duplicate artifact ID: {ident}")
        digest = a.get("sha256")
        if digest is not None and (not isinstance(digest, str) or not DIGEST.fullmatch(digest)):
            raise AcquisitionError(f"Invalid pinned SHA-256 for {ident}")
        found[ident] = a
    return obj, found


def output_filename(name: str | None, url: str | None, source: Path | None = None) -> str:
    if name is None:
        if source is not None:
            name = source.name
        elif url is not None:
            name = urllib.parse.unquote(Path(urllib.parse.urlparse(url).path).name)
    if not name or name in {".", ".."} or not SAFE_NAME.fullmatch(name) or "/" in name or "\\" in name:
        raise AcquisitionError("Cannot safely infer filename; pass --name <file.zip|file.st|...>")
    return name


class SecureRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urllib.parse.urlparse(newurl).scheme != "https":
            raise AcquisitionError("Refusing redirect to a non-HTTPS URL")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def transfer_url(url: str, dst: Path, max_bytes: int = MAX_BYTES):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise AcquisitionError("Direct download URL must use HTTPS (no embedded credentials)")
    req = urllib.request.Request(url, headers={"User-Agent": "obasic-research/0.1", "Accept": "application/octet-stream,application/zip,*/*"})
    opener = urllib.request.build_opener(SecureRedirect())
    with opener.open(req, timeout=45) as resp, dst.open("wb") as out:
        content_type = resp.headers.get("Content-Type", "").lower()
        if "text/html" in content_type:
            raise AcquisitionError("Server sent an HTML page, not an archive: check the direct URL")
        length = 0
        first = b""
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            if not first:
                first = chunk[:256].lstrip().lower()
                if first.startswith((b"<!doctype html", b"<html", b"<?xml")):
                    raise AcquisitionError("Response resembles an HTML/XML page, not an archive")
            length += len(chunk)
            if length > max_bytes:
                raise AcquisitionError(f"Download exceeds {max_bytes} bytes")
            out.write(chunk)
        if not length:
            raise AcquisitionError("Empty downloaded artifact")
        final = resp.geturl()
        if urllib.parse.urlparse(final).scheme != "https":
            raise AcquisitionError("Final URL is not HTTPS")
        return final, content_type


def acquire(a, dest: Path, *, url: str | None, file: Path | None,
            name: str | None, allow_unpinned: bool):
    expected = a.get("sha256")
    if not expected and not allow_unpinned:
        raise AcquisitionError(f"{a['id']} has no pinned SHA-256: first use --allow-unpinned; inspect, then pin")
    if file is None and not url:
        raise AcquisitionError(f"{a['id']} has no direct download URL; use --url or edit artifacts/sources.json")
    if file is not None and not file.is_file():
        raise AcquisitionError(f"Missing input file: {file}")
    filename = output_filename(name, url, file)
    folder = dest / a["id"]
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / filename
    if target.exists():
        raise AcquisitionError(f"Refusing to overwrite existing file: {target}")
    fd, tmppath = tempfile.mkstemp(prefix=".download-", dir=folder)
    os.close(fd)
    tmp = Path(tmppath)
    final_url, content_type = None, None
    try:
        if file is not None:
            if file.stat().st_size > MAX_BYTES or file.stat().st_size == 0:
                raise AcquisitionError("Input file is empty or larger than 100 MiB")
            shutil.copyfile(file, tmp)
        else:
            final_url, content_type = transfer_url(url, tmp)
        actual = sha256(tmp)
        if expected and actual != expected:
            raise AcquisitionError(f"SHA-256 mismatch, expected {expected}, got {actual}")
        tmp.rename(target)
        receipt = {
            "schema": 1, "artifact_id": a["id"], "target": a["target"], "role": a["role"],
            "source_page": a.get("catalog_url"), "requested_url": url,
            "final_url": final_url, "content_type": content_type,
            "imported_from": str(file.resolve()) if file is not None else None,
            "filename": target.name, "bytes": target.stat().st_size,
            "sha256": actual, "pinned": actual == expected,
            "collected_utc": datetime.now(timezone.utc).isoformat(),
            "note": "Original artifact; do not commit/re-distribute by default. No archive extraction performed."
        }
        receipt_path = target.with_name(target.name + ".receipt.json")
        receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return target, receipt
    finally:
        tmp.unlink(missing_ok=True)


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--registry", type=Path, default=REGISTRY)
    p.add_argument("--store", type=Path, default=STORE)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List candidates and pin state")
    for cmd in ("fetch", "import"):
        c = sub.add_parser(cmd, help=f"{cmd} artifact without automatic extraction")
        c.add_argument("id")
        if cmd == "fetch":
            c.add_argument("--url", help="Verified direct HTTPS artifact URL (overrides registry)")
        else:
            c.add_argument("--file", type=Path, required=True, help="Local original disk/archive")
        c.add_argument("--name", help="Safe output filename, use when URL does not identify file type")
        c.add_argument("--allow-unpinned", action="store_true", help="Allow initial discovery before pinning SHA-256")
    c = sub.add_parser("pin", help="Pin one already acquired artifact after manually inspecting it")
    c.add_argument("id")
    c.add_argument("--file", type=Path, required=True)
    c.add_argument("--url", help="Also store a vetted direct HTTPS download URL")
    c = sub.add_parser("verify", help="Check a local artifact against its recorded hash")
    c.add_argument("id")
    c.add_argument("--file", type=Path, required=True)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        obj, items = registry(args.registry)
        if args.command == "list":
            for a in items.values():
                status = "pinned" if a.get("sha256") else "unverified"
                download = "direct URL" if a.get("url") else "needs URL/local file"
                print(f"{a['id']:<25} {status:<11} {download} | {a['description']}")
            return 0
        if args.id not in items:
            raise AcquisitionError(f"Unknown artifact: {args.id}; run list first")
        a = items[args.id]
        if args.command == "pin":
            if not args.file.is_file() or not args.file.stat().st_size:
                raise AcquisitionError("Pin source must be an existing, nonempty file")
            newhash = sha256(args.file)
            if a.get("sha256") and a["sha256"] != newhash:
                raise AcquisitionError("Different pin already exists; review manually before changing the manifest")
            if args.url:
                parsed = urllib.parse.urlparse(args.url)
                if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
                    raise AcquisitionError("Pinned URL must be HTTPS with no embedded credentials")
                a["url"] = args.url
            a["sha256"] = newhash
            a["size"] = args.file.stat().st_size
            args.registry.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"PINNED {a['id']} SHA256 {newhash} size={a['size']}")
            return 0
        if args.command == "verify":
            if not a.get("sha256"):
                raise AcquisitionError("Artifact is not pinned; run pin after checking it")
            if not args.file.is_file():
                raise AcquisitionError("Missing local file")
            digest = sha256(args.file)
            if digest != a["sha256"]:
                raise AcquisitionError(f"Mismatch: {digest} != {a['sha256']}")
            print(f"VERIFIED {a['id']} SHA256 {digest}")
            return 0
        url = (args.url or a.get("url")) if args.command == "fetch" else None
        file = args.file if args.command == "import" else None
        target, receipt = acquire(a, args.store, url=url, file=file,
                                  name=args.name, allow_unpinned=args.allow_unpinned)
        status = "verified" if receipt["pinned"] else "UNPINNED — inspect before pinning"
        print(f"{status}: {target}\nSHA256 {receipt['sha256']}\nreceipt {target}.receipt.json")
        return 0
    except (AcquisitionError, OSError, ValueError, urllib.error.URLError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
