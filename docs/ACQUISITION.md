# Historical material — acquisition and provenance

## Principles

Keep proprietary originals and full disassemblies under ignored `work/`.
Never infer a download endpoint from a catalog page, or pin an unverified hash.
Record disk image hashes separately from hashes of extracted executables.
Before publication, review the applicable rights: archive availability is not a license.

## Research starting points

- Turbo-BASIC XL historical material: https://www.atariwiki.org/wiki/Wiki.jsp?page=Turbo-BASIC+XL
- Turbo-BASIC XL reconstructed MADS listing: https://github.com/dmsc/turbo-dis
- GFA 1.0 catalog: https://www.atarimania.com/games/atari-st-utilities-gfa-basic-38892
- GFA BASIC catalogs and compilers: https://www.atariuptodate.de/en/progs/gfabasic
- `rg-dis` manual: https://rg.atari.org/tools/rg-dis/readme.html

These URLs are research leads, not confirmed direct download links.

## Workflow

List known candidates:

```sh
make sources
```

Acquire a verified direct HTTPS file, or import a disk image you obtained manually:

```sh
python3 tools/acquire.py fetch gfa-2.02-disk --url https://HOST/FILE.st --allow-unpinned
python3 tools/acquire.py import gfa-1.0-disk --file /path/to/disk.st --allow-unpinned
```

Inspect the release, then pin the archive bytes in `artifacts/sources.json`:

```sh
python3 tools/acquire.py pin gfa-2.02-disk --file work/originals/gfa-2.02-disk/FILE.st
python3 tools/acquire.py verify gfa-2.02-disk --file work/originals/gfa-2.02-disk/FILE.st
git diff -- artifacts/sources.json
```

Paths and URLs in these examples are placeholders, not verified artifact locations.

Every acquisition produces a JSON receipt with source, SHA-256, size, and date.
Original bytes are not automatically extracted, executed, or committed.
Download only when the source permits automated access; do not bypass authorization.

## Execution

`rg_batch.py` intentionally accepts extracted 68000 executables, not floppy images.
Inspect/extract Atari ST `.ST`/`.MSA` images separately before disassembly.
`rg-dis` is not a 6502 disassembler: use MADS and 6502 tools for Turbo-BASIC XL.
