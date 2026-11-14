#!/usr/bin/env python3
"""Capture reproducible rg-dis evidence for extracted GFA 68000 binaries."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {"gfa-1.0": "st", "gfa-2.02": "st", "gfa-3.02": "st", "gfa-3.60": "st", "gfa-3.6tt": "tt"}
ROLES = ("interpreter", "compiler", "runtime", "linked-program", "utility")
DISK_EXTS = {".st", ".msa", ".stx", ".atr", ".xfd", ".zip", ".lzh", ".car", ".rom"}
EXEC_EXTS = {".prg", ".tos", ".app", ".gtp", ".ttp", ".acc", ".o", ".obj", ".cpx"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--target", choices=[*TARGETS, "tbxl-1.5"], required=True)
    p.add_argument("--role", choices=ROLES, required=True)
    p.add_argument("--input", type=Path, required=True, help="extracted executable, not a disk image")
    p.add_argument("--source-note", default="UNRECORDED: provenance still needed")
    p.add_argument("--rg", default="rg-dis", help="rg-dis executable")
    p.add_argument("--raw-origin", help="origin for headerless m68k binary, e.g. 0x10000")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args(argv)


def validate(args):
    if args.target == "tbxl-1.5":
        raise ValueError("Turbo-BASIC XL is 6502, and rg-dis only handles 680x0 / DSP, not 6502")
    path = args.input.expanduser().resolve()
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"Missing/empty input: {path}")
    if path.suffix.lower() in DISK_EXTS:
        raise ValueError("disk image/archive refused: extract the 68000 executable first")
    if args.raw_origin is None:
        if path.suffix.lower() not in EXEC_EXTS:
            raise ValueError("Unknown executable type: supply --raw-origin only for a headerless 68000 dump")
        if path.suffix.lower() in {".prg", ".tos", ".app", ".gtp", ".ttp", ".acc"}:
            with path.open("rb") as fd:
                magic = fd.read(2)
            if magic != b"\x60\x1a":
                raise ValueError("Invalid GEMDOS PRG magic; inspect file format before disassembling")
    else:
        try:
            addr = int(args.raw_origin, 0)
        except ValueError as e:
            raise ValueError("--raw-origin requires decimal or 0x-prefixed hex address") from e
        if not 0 <= addr <= 0xffffffff or path.suffix.lower() in EXEC_EXTS:
            raise ValueError("--raw-origin invalid: use a 32-bit origin with a raw dump")
    return path


def commands(exe: str, inp: Path, args, out: Path):
    common = [exe, str(inp), "--arch", "68k", "--cpu", "auto", "--machine", TARGETS[args.target],
              "--dialect", "vasm", "--quiet"]
    if args.raw_origin is not None:
        common += ["--input-format", "raw", "--org", args.raw_origin]
    annotate = ["--no-annotate-gfa"] if args.target == "gfa-1.0" else ["--annotate-gfa"]
    steps = [
        ("asm", common + annotate + ["--json", "-o", str(out / "disasm.s")]),
        ("inspect", common + ["--inspect", "--json"]),
        ("functions", common + ["--inspect", "functions,cycles", "--json"]),
        ("strings", common + ["--inspect", "strings", "--json"]),
        ("regions", common + ["--inspect", "regions", "--record-decisions", "--json"]),
    ]
    if args.target != "gfa-1.0":
        steps.append(("baseline", common + ["--no-annotate-gfa", "--json", "-o", str(out / "baseline.s")]))
    return steps


def main(argv=None):
    args = parse_args(argv)
    try:
        inp = validate(args)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    executable = shutil.which(args.rg)
    if executable is None:
        print("error: rg-dis not installed; https://rg.atari.org/tools/rg-dis/", file=sys.stderr)
        return 2
    exe = str(Path(executable).resolve())
    try:
        v = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if v.returncode:
        print("error: rg-dis --version failed", file=sys.stderr)
        return 2
    version = (v.stdout or v.stderr).strip()
    tag = re.sub(r"[^a-zA-Z0-9_.-]+", "-", version).strip("-")[:64] or "unknown"
    digest = sha256(inp)
    out = ROOT / "work" / "rg" / args.target / args.role / digest[:12] / tag
    steps = commands(exe, inp, args, out)
    if args.dry_run:
        print(f"SHA256 {digest}  {inp}\nTOOL {version}\nOUTPUT {out} (not created)")
        for label, cmd in steps:
            print(f"{label}: {shlex.join(cmd)}")
        return 0
    out.mkdir(parents=True, exist_ok=True)
    receipt = {
        "schema": 1, "target": args.target, "role": args.role,
        "input": {"filename": inp.name, "path": str(inp), "size": inp.stat().st_size,
                  "sha256": digest, "source_note": args.source_note},
        "tool": {"name": "rg-dis", "version": version, "path": exe, "sha256": sha256(Path(exe))},
        "utc": datetime.now(timezone.utc).isoformat(), "commands": [], "complete": False,
        "note": "Machine output: not validated historical source reconstruction.",
    }
    failed = False
    try:
        for label, cmd in steps:
            r = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=900)
            (out / f"{label}.json").write_text(r.stdout, encoding="utf-8")
            (out / f"{label}.stderr.txt").write_text(r.stderr, encoding="utf-8")
            try:
                json.loads(r.stdout)
                valid_json = True
            except json.JSONDecodeError:
                valid_json = False
            receipt["commands"].append({"step": label, "argv": cmd, "returncode": r.returncode,
                                        "json_valid": valid_json})
            if r.returncode or not valid_json:
                failed = True
                print(f"FAIL {label}: exit={r.returncode} json={valid_json}", file=sys.stderr)
            else:
                print(f"OK   {label}")
    except (OSError, subprocess.TimeoutExpired) as e:
        failed = True
        receipt["error"] = repr(e)
    finally:
        receipt["complete"] = not failed
        (out / "receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Evidence directory: {out}")
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
