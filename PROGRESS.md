# PROGRESS

## Current phase

P3-C remains incomplete. P3-C2 established exact direct-mode keyboard input and a
first natural parser-to-dispatch observation for three PRINT examples. H0 prepares the
Pi transfer; it does not execute P3-C3.

## Completed milestones

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

## Pending

- First real Pi session: verify extension startup, actual prompt/context loading, and
  Handoff status. This has not been attested.
- P3-C3/1: trace only the natural target TEXT `$5D04` through immediate output paths
  for the two existing PRINT inputs, E/D; see `HANDOFF.md`.

## Blockers and limits

Pi 1.5.2 and context-guard files are locally available, but there was no installed Pi
package or prior obasic Handoff state. Startup was not yet confirmed in a Pi session.
The selected runtime target's general function is unknown; P3-C is not complete.
