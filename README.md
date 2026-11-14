# obasic — archaeology of Ostrowski BASICs

Reconstruct and document the original Atari BASIC interpreters/compilers, then develop independent, maintainable successors. Byte-identical reproduction is **not** a goal.

## Scope

| Target | CPU | Historical material | Primary archaeology tool |
| --- | --- | --- | --- |
| `tbxl-1.5` | MOS 6502 | Turbo-BASIC XL 1.5; compiler 1.1; runtime | Existing MADS disassembly + 6502 emulator |
| `gfa-1.0` | Motorola 68000 | GFA BASIC 1.0 interpreter, run-only runtime; associated compiler to inventory | `rg-dis` general 68000 disassembly |
| `gfa-2.02` | Motorola 68000 | GFA BASIC 2.02 and compiler/runtime | `rg-dis`, GFA recognition where applicable |
| `gfa-3.02` | Motorola 68000 | GFA BASIC 3.02 and compiler/runtime | `rg-dis`, GFA recognition where applicable |
| `gfa-3.60` | Motorola 68000 | GFA BASIC 3.60 and compiler/runtime | `rg-dis`, GFA recognition where applicable |
| `gfa-3.6tt` | Motorola 68000/TT | GFA BASIC 3.6TT and compiler/runtime | `rg-dis`, GFA recognition where applicable |

STOS is deliberately not in the first phase; its future track can share the Atari ST tooling.

## Two deliverables per system

1. **`reconstruction/`**: documented historical algorithms, supported by the exact binary, addresses and observations; no automatic claims of historical source-code identity.
2. **`modern/`**: clean implementation with explicit compatibility and extended modes, independently tested against original behavior.

**`work/` is ignored**: original commercial binaries, full machine-code listings, machine-generated artifacts, and logs stay local until provenance and publication rights have been assessed. The repository tracks reproducible commands, evidence indexes, and original analysis, not third-party code by default.

## Historical artifacts: reproducible acquisition

The tracked [`artifacts/sources.json`](artifacts/sources.json) contains research leads and SHA-256 pins; `tools/acquire.py` fetches direct HTTPS URLs or imports manually acquired files into ignored `work/originals/` with provenance receipts. Original binaries are not committed. See [`docs/ACQUISITION.md`](docs/ACQUISITION.md).

```sh
make sources
python3 tools/acquire.py import gfa-1.0-disk --file /path/to/disk.st --allow-unpinned
```

## Generate GFA evidence

Install `rg-dis` from <https://rg.atari.org/tools/rg-dis/>. Record the exact release; v0.11.46 was current when this skeleton was prepared (2026-11-14). Put the *extracted 68000 executable* (`.PRG`, `.TOS`, `.APP`, etc.) in a directory of your choice, then:

```sh
python3 tools/rg_batch.py --target gfa-2.02 --role interpreter \
  --input /path/to/GFA.PRG --source-note 'My original disk / verified archive'
python3 tools/rg_batch.py --target gfa-2.02 --role compiler \
  --input /path/to/COMPILER.PRG --source-note 'My original disk / verified archive'
```

This generates `work/rg/<target>/<role>/<sha12>/` with `.s` listing, structured inspection JSON, function and string listings, and `receipt.json` (tool version, input hash, arguments, return codes). These files are **not** auto-committed.

To preview without running a tool:

```sh
python3 tools/rg_batch.py --target gfa-3.60 --role runtime \
  --input /path/to/RUNTIME.PRG --dry-run
```

`rg-dis` is not a 6502 disassembler. For Turbo-BASIC XL, use [the pre-existing MADS disassembly](https://www.atariwiki.org/wiki/Wiki.jsp?page=Turbo-BASIC+XL) and the dedicated [dmsc/turbo-dis project](https://github.com/dmsc/turbo-dis) as candidate references, with author and license verification. Preserve its provenance; it is not automatically part of this repository.

## Workflows

- Read [`docs/ACQUISITION.md`](docs/ACQUISITION.md) before collecting binaries.
- Read [`docs/SCIENTIFIC_PROTOCOL.md`](docs/SCIENTIFIC_PROTOCOL.md) before making claims.
- Read [`AGENTS.md`](AGENTS.md) and the [agent briefs](docs/AGENT_KICKOFF.md) before starting an autonomous Codex / Sushi agent.
- Check CLI locally with `python3 -m unittest discover -s tests -v`.
- No GitHub remote is created by this local skeleton.
