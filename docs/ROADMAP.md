# Initial campaign (not yet executed on historical binaries)

## R0 — toolchain and inventory

- [x] Scaffold `obasic` with separate architecture tracks.
- [x] Deterministic rg-dis wrapper, private outputs, self-tests.
- [ ] Supply and hash verified historical executables (GFA 1.0, 2.02, 3.02, 3.60/3.6TT).
- [ ] Verify interpreter / compiler / runtime versions independently.
- [ ] Verify status, provenance and license of Turbo-BASIC XL MADS source.
- [ ] Run rg-dis v0.11.46 (or pin actual chosen version) on extracted GFA executables.

## R1 — comparative archaeological atlas

- [ ] Produce GFA 1.0 vs 2.x vs 3.x startup/dispatch/routines maps.
- [ ] Classify routine names: rg-dis signature / manually proved / unresolved.
- [ ] For TBXL, map tokenizer, parser, expression evaluator against MADS listing.
- [ ] Identify small, verifiable vertical slice per language.

## R2 — implementations

- [ ] Source reconstruction by subsystem with high-quality comments.
- [ ] Modern frontend and semantic engine with strict and extended modes.
- [ ] Atari emulators as differential oracles; native backend exploration after semantic tests.

## R3 — STOS (future)

- [ ] Archive original STOS versions and compile outputs.
- [ ] Reuse rg-dis and Hatari oracle; add graphics, audio and input traces.
