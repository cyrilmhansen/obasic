# HANDOFF

## Recovery instructions

Read this file and `PROGRESS.md` first. `AGENTS.md` is the project contract. Consult
`LEARNINGS.md` for scientific invariants and `PROTOCOL.md` when planning experiments.
Raw binaries, ROMs and Hatari captures stay in `work/`; do not load them into initial
context. Evidence reports remain the authority for historical claims.

## Last verified state

P3-C3 is the latest validated scientific milestone (reports in `analysis/gfa/`): the two
natural PRINT inputs enter TEXT `$5D04` (`$14608`, base `$E904`) under E and D with the
byte-exact P3-C2 parser inputs; the entry stack carries the return address `$104F2`
(TEXT+`$1BEE`, proving the C2 indirect `JSR (A0)`); the first 512 bytes of the target body
were captured byte-identical across all runs and E/D (SHA-256 `078234b7…`), disassembled
reproducibly with pinned rg-dis 0.11.46; and the natural output boundary was proven: all
four `output` runs reach TEXT+`$5E36` (immediately after the BIOS `TRAP #13` Bconout,
dev=2 console) with the printed character (`A`/`3`) in the stack capture and the return
chain `$11070→$14650→$104F2`. Single-stepping the body failed (recorded as falsified
evidence: Hatari resumes emulation before the first FIFO step). The dynamic instruction
order inside the body is UNMEASURED; the target is still unnamed. P3-C remains incomplete
(scanner `$12EF6`, P3-B tables unobserved).

## Unfinished operations

Pi Handoff is newly prepared from local context-guard `0.1.0-rc.1` source; no obasic
checkpoint, attestation or renewal chain has been initialized. The first Pi session must
inspect its startup status and context-cost report. Do not infer a valid checkpoint or
chain from missing state. Session 01a1db73 (2026-11-14) inspected startup: extension
loaded, `handoff_inspect` reported checkpoint missing, renewal disabled, `make test`
25/25 OK. The agent has aligned HANDOFF/PROGRESS/LEARNINGS to the guard's required
section headings; `handoff_finalize` still refuses because `GOAL.md` lacks
`## Objective` and `## Acceptance criteria` headings (protected file; see
LEARNINGS.md Proposed). **Operator action:** apply the two-line heading rename in
`GOAL.md`, then the agent can finalize the first checkpoint.

## Next action

**Await operator direction.** P3-C3/1 is closed with its documented limits (see
`analysis/gfa/P3C3_HANDOFF.md`). Options recorded but NOT started: (a) chained
`:trace :once` per-instruction breakpoints to recover the body's dynamic order, (b)
read-watchpoints on the body's format fields during natural continuation, or (c) proceed
to P3-D keeping the target unnamed. Do not start P3-D without explicit operator approval.

Also open, operator-side: rename `GOAL.md` headings to `## Objective` / `## Acceptance
criteria` (see LEARNINGS.md Proposed) so checkpoint attestation passes.

## Discoveries not yet incorporated

Hatari 2.6.1 `:file`/interactive FIFO stepping cannot halt at the natural target entry:
the emulator resumes and finishes the line before the first `hatari-debug c 1` (see
NATURAL_EXECUTION_36_C3.md, Falsified section). No semantic discovery beyond
`LEARNINGS.md` and the P3-C3 evidence reports.

## Constraints

Preserve `artifacts/sources.json` and all pre-existing operator edits. Do not modify P1,
P2 or P3-A through P3-C2 evidence. Keep work artifacts ignored, use explicit Git paths,
run `make test` and `git diff --check`, and do not push. Keep Handoff renewal and automatic
renewal disabled unless the operator separately authorizes their activation.

References: `analysis/gfa/P3C3_HANDOFF.md`,
`analysis/gfa/NATURAL_EXECUTION_36_C3.md`,
`analysis/gfa/NATURAL_EXECUTION_36_C3_DATA.json`, and the earlier P3-A/P3-B/P3-C2 reports
linked from `analysis/gfa/P3C2_HANDOFF.md`.
<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 3
checkpoint-id: g3-6aae25020c88
checkpoint-kind: auto
content-delta: new
readiness: unattested
status: checkpoint (guard level 3, remaining ~9120, session 01a1dc29-4525-7386-b21c-5306536e80b9)
checkpointed: 2026-11-15T07:45:39.702Z
source-goal: b3b8726a43fed9e764858f945b07655125e0a9acb392a8e6a161ee1c8affba37
source-progress: 83ca76a7c39c846b4862e0208ec84ca5590895f49807d6b38df3c9f2a9fc0dba
source-handoff: 7f4f2ec12a7a33a62f6c386249374474f40e50f7ef3817d1dac419741be1efc3
source-learnings: 15f53eab712301352a51666cc6967b034b809a871edcc18fa1e1da71f8c5760f
source-config: ec61426c39667346e3f0370be688b0523ad5d7941de4d913a9bf0618f785e08c


### Last verified state
guard level 3; checkpoint requested (auto at level 3)

### Unfinished operations
- (none recorded)

### Next action
**Await operator direction.** P3-C3/1 is closed with its documented limits (see
`analysis/gfa/P3C3_HANDOFF.md`). Options recorded but NOT started: (a) chained
`:trace :once` per-instruction breakpoints to recover the body's dynamic order, (b)
read-watchpoints on the body's format fields during natural continuation, or (c) proceed
to P3-D keeping the target unnamed. Do not start P3-D without explicit operator approval.

Also open, operator-side: rename `GOAL.md` headings to `## Objective` / `## Acceptance
criteria` (see LEARNINGS.md Proposed) so checkpoint attestation passes.
<!-- guard:end checkpoint -->
