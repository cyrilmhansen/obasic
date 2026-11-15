# PROGRESS

## Current phase

P3-C remains incomplete. P3-C2 established exact direct-mode keyboard input and a
first natural parser-to-dispatch observation. P3-C3 bounded the target TEXT `$5D04`:
natural entry, 512-byte body capture and reproducible rg-dis listing, and the natural
Bconout output boundary at TEXT+`$5E36`, E/D identical for the two PRINT cases. P3-D is
NOT started; operator direction required.

## Completed

- P1: structural 3.6TT D/E compiler comparison; shared instruction base measured, not
  behavioral equivalence. `analysis/gfa/COMPILER_36_DE.md`.
- P2: inventory and cross-generation lineage map. `analysis/gfa/INVENTORY.md`,
  `analysis/gfa/LINEAGE.md`, `analysis/gfa/LINEAGE_DATA.json`.
- P3-A: startup reconstructed to dispatcher boundary. `analysis/gfa/STARTUP_36.md`.
- P3-B: generated text/token spelling maps reconstructed and matched to captures;
  natural parser path then remained unproved. `analysis/gfa/TOKEN_TABLES_36.md`.
- P3-C initial: malformed `PRINT 3A3` exposed keyboard mapping error;
  `analysis/gfa/NATURAL_EXECUTION_36.md`.
- P3-C2: scancode calibration; `PRINT`, `PRINT "A"`, `PRINT 1+2` byte-exact and
  accepted under E/D; outputs blank, `A`, `3`; all six reached `$1BD6`/`$1BEC` and
  selected `$14608`. See `analysis/gfa/NATURAL_EXECUTION_36_C2.md` and its JSON.
- P3-C3: natural entry to `$14608` proven via return address `$104F2` (TEXT+`$1BEE`);
  body 512 bytes captured, identical E/D (`078234b7…`), rg-dis 0.11.46 listing reproduced
  byte-exact; output boundary TEXT+`$5E36` (after `TRAP #13` Bconout dev=2) reached by
  natural continuation in all four `output` runs with printed character in stack capture;
  screens `A`/`3` + `OK >`. Single-step of the body falsified (see report). Evidence:
  `analysis/gfa/NATURAL_EXECUTION_36_C3.md`, `NATURAL_EXECUTION_36_C3_DATA.json`,
  `P3C3_HANDOFF.md`; raw files under `work/p3c3/`.

## Verified evidence

- P3-C3 raw evidence (8 runs: fixtures, traces, logs, screenshots, hashes incl. all 150
  files in the JSON): `work/p3c3/`; drivers `run_target_case.py`, `run_steps2.py`;
  listing `target-body-5d04.s`. Input bytes match P3-C2 hashes exactly.
- P3-C2 raw evidence (parser buffers, dispatch/capture files, screenshots, hashes):
  `work/p3c2/` and `analysis/gfa/NATURAL_EXECUTION_36_C2_DATA.json`; profile
  `tools/hatari_gfa_scancode.cfg`. First Pi session bootstrap: extension loaded in
  session 01a1db73 (diagnostics `session_start`), `make test` 25/25 OK.

## Next action

Await operator direction (options in `HANDOFF.md`): recover the body's dynamic
instruction order via chained `:trace :once` breakpoints or read-watchpoints, or proceed
to P3-D. Operator-side: `GOAL.md` heading rename so checkpoint attestation passes.

## Pending

- Operator: rename `GOAL.md` headings (`## Objective`, `## Acceptance criteria`) so
  checkpoint attestation can pass; then re-run `/handoff finalize`.
- Recover the body's dynamic instruction order (chained `:trace :once` breakpoints or
  read-watchpoints) — only with operator direction.
- P3-C completion items: `$12EF6` scanner observation, P3-B tables, naming `$5D04`.

## Blockers

Pi 1.5.2 and context-guard files are locally available. Hatari 2.6.1 interactive/FIFO
stepping could not halt the guest at the natural target entry (falsified, recorded);
the target's dynamic execution order and general function remain unknown; P3-C is not
complete.
<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 5
checkpoint-id: g5-199822e892b0
checkpoint-kind: manual
content-delta: new
readiness: unattested
guard-level: 0
checkpointed: 2026-11-15T07:55:07.453Z
source-goal: b3b8726a43fed9e764858f945b07655125e0a9acb392a8e6a161ee1c8affba37
source-progress: c4c48abf0015352d9c46d61d176df6086ab381e42e4eba041650087a7cc56d8f
source-handoff: 7f4f2ec12a7a33a62f6c386249374474f40e50f7ef3817d1dac419741be1efc3
source-learnings: cdad39cbc661d942c3b25e2c91f12cc193e11899b52345aa70d02a23d51c470c
source-config: ec61426c39667346e3f0370be688b0523ad5d7941de4d913a9bf0618f785e08c
next-action: **Await operator direction.** P3-C3/1 is closed with its documented limits (see
`analysis/gfa/P3C3_HANDOFF.md`). Options recorded but NOT started: (a) chained
`:trace :once` per-instruction breakpoints to recover the body's dynamic order, (b)
read-watchpoints on the body's format fields during natural continuation, or (c) proceed
to P3-D keeping the target unnamed. Do not start P3-D without explicit operator approval.

Also open, operator-side: rename `GOAL.md` headings to `## Objective` / `## Acceptance
criteria` (see LEARNINGS.md Proposed) so checkpoint attestation passes.
<!-- guard:end checkpoint -->
