# HANDOFF

## Recovery instructions

Read this file and `PROGRESS.md` first. `AGENTS.md` is the project contract. Consult
`LEARNINGS.md` for scientific invariants and `PROTOCOL.md` when planning experiments.
Raw binaries, ROMs and Hatari captures stay in `work/`; do not load them into initial
context. Evidence reports remain the authority for historical claims.

## Last verified state

P3-C2 is the latest validated scientific milestone at baseline commit
`14c3b964a56d9ada7681998e9d02a2e83ead3046`: E and D accepted the three naturally typed
PRINT forms and displayed blank, `A`, and `3`. All six valid runs reached TEXT `$1BD6`
and indirect `JSR (A0)` at `$1BEC`, selecting runtime `$14608` (TEXT `$5D04` at observed
base `$E904`). The target body remains unreconstructed. P3-C is incomplete.

## Unfinished operations

Pi Handoff is newly prepared from local context-guard `0.1.0-rc.1` source; no obasic
checkpoint, attestation or renewal chain has been initialized. The first Pi session must
inspect its startup status and context-cost report. Do not infer a valid checkpoint or
chain from missing state.

## Next action

**P3-C3/1 — trace the natural PRINT target.** Start Pi with the command in
`docs/PI_MIGRATION.md`, inspect `/guard status` and `handoff_inspect`, then use only the
P3-C2 inputs `PRINT "A"` and `PRINT 1+2`. From the observed TEXT base, trace a bounded
portion of TEXT `$5D04` through immediate output dependencies under E and D. Stop before
generalizing the target's role or rebuilding PRINT/parser behavior.

Acceptance: each run proves natural entry to the target with the correct input, records
the first bounded target instructions/calls and output boundary, compares E/D using the
same TOS 3.06 TT profile and input bytes, and cites raw trace hashes under `work/`. Add a
partial historical reconstruction with unknown paths explicit. No parser-buffer or
register injection; no semantic claim beyond these two cases.

## Constraints

Preserve `artifacts/sources.json` and all pre-existing operator edits. Do not modify P1,
P2 or P3-A through P3-C2 evidence. Keep work artifacts ignored, use explicit Git paths,
run `make test` and `git diff --check`, and do not push. Keep Handoff renewal and automatic
renewal disabled unless the operator separately authorizes their activation.

References: `analysis/gfa/P3C2_HANDOFF.md`,
`analysis/gfa/NATURAL_EXECUTION_36_C2.md`,
`analysis/gfa/NATURAL_EXECUTION_36_C2_DATA.json`, and the earlier P3-A/P3-B reports linked
from `analysis/gfa/P3C2_HANDOFF.md`.
