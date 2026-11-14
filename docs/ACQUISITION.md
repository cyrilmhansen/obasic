# Source acquisition and provenance

## Inventory first

For each language version, gather separately: interpreter/editor, compiler, run-only runtime, linked runtime libraries, manuals and examples. Some releases have separate localization or patches. **Do not infer a matching compiler exists from the interpreter version number.**

For every file, record: source URL or physical medium, collector, date, version as displayed, filename, length, SHA-256, packaging/container, and a licensing/publication decision. Put proprietary originals under `work/originals/` (ignored).

## Research starting points

- Turbo-BASIC XL MADS disassembly and historical magazine sources: <https://www.atariwiki.org/wiki/Wiki.jsp?page=Turbo-BASIC+XL>
- dmsc original project with reconstructed MADS interpreter: <https://github.com/dmsc/turbo-dis>
- MADS 6502 cross-assembler and project list: <https://github.com/tebe6502/Mad-Assembler>
- GFA 1.0 archival entry (commercial): <https://www.atarimania.com/games/atari-st-utilities-gfa-basic-38892>
- GFA 2.02 / GFA 3.x archive catalog: <https://www.atariuptodate.de/en/progs/gfabasic>
- rg-dis documentation: <https://rg.atari.org/tools/rg-dis/readme.html>
- rg-dis release notes: <https://rg.atari.org/tools/rg-dis/release-notes.html>

These are **leads, not license grants**. Verify hashes, dates and whether materials can be redistributed. Default: keep commercial binary and derived full disassembly private.

## Extraction rule

`rg-dis` can inspect disk images and read archives, but `rg_batch.py` intentionally accepts **only extracted executable/object files**. First inspect `.ST` / `.MSA` / `.STX` via `rg-dis disk.st --inspect disk`, then extract the relevant `GFA*.PRG` / `*.TOS` file using a separate tool. The source disk is not equivalent to a single program.

For Atari 8-bit TBXL, the MADS listing is a historical reverse-engineering reference. Do not run `rg-dis` over the TBXL 6502 object code; it would interpret it as 68000 and produce bogus output.
