# PROGRESS

## Current phase

P3-D/1 is complete with explicit limits. P3-C3's target TEXT `$5D04` was statically
graphed and partially reconstructed. Natural E/D runs for both PRINT cases reach the
Bconout boundary at TEXT+`$5E36`; internal block order and general semantics remain
UNMEASURED.

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

**P3-D/1 is finished with limits.** Preserve the new report, JSON, handoff,
reconstruction and `work/p3d1/`. Any continuation must first obtain reliable natural
block-order instrumentation; do not infer missing blocks.

## Pending

- Future optional work: obtain reliable natural block-order and field-value instrumentation.
- P3-C completion items remain separate: `$12EF6` scanner observation, P3-B tables, naming
  `$5D04`.

## Blockers

No blocker for the bounded P3-D/1 deliverable. Hatari 2.6.1 interactive/FIFO stepping
and the candidate-block probe did not yield ordered intermediate execution; this is a
recorded limit, not evidence of absent blocks.
<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 6
checkpoint-id: g6-abc1668752fc
checkpoint-kind: manual
content-delta: new
readiness: attested
guard-level: 0
checkpointed: 2026-11-15T08:16:08.048Z
source-goal: cf78d67219ee2fe666f7f42456db99568d8a5ec13609e034ac86771a73edf102
source-progress: c4c48abf0015352d9c46d61d176df6086ab381e42e4eba041650087a7cc56d8f
source-handoff: 7f4f2ec12a7a33a62f6c386249374474f40e50f7ef3817d1dac419741be1efc3
source-learnings: 1021e1a81f1847511707836b4e2f8c0974766b9872625ac3a53bd0b993a75be2
source-config: 37f26ea8df3ae379db57044849c73851c3d7822b1a09fe4b2c2a59f1b4542707
next-action: **Await operator direction.** P3-C3/1 is closed with its documented limits (see
`analysis/gfa/P3C3_HANDOFF.md`). Options recorded but NOT started: (a) chained
`:trace :once` per-instruction breakpoints to recover the body's dynamic order, (b)
read-watchpoints on the body's format fields during natural continuation, or (c) proceed
to P3-D keeping the target unnamed. Do not start P3-D without explicit operator approval.

Also open, operator-side: rename `GOAL.md` headings to `## Objective` / `## Acceptance
criteria` (see LEARNINGS.md Proposed) so checkpoint attestation passes.
readiness-by: session:01a1de46-d8ab-752e-ab82-adc4a8c41642
readiness-at: 2026-11-15T08:16:08.052Z
readiness-checkpoint: g6-abc1668752fc
<!-- guard:end checkpoint -->
