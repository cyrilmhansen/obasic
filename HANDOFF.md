# HANDOFF

## Recovery instructions

Read this file and `PROGRESS.md` first. `AGENTS.md` is the project contract. Consult
`LEARNINGS.md` for scientific invariants and `PROTOCOL.md` when planning experiments.
Raw binaries, ROMs and Hatari captures stay in `work/`; do not load them into initial
context. Evidence reports remain the authority for historical claims.

## Last verified state

P3-D/2 is the latest bounded milestone. Hatari 2.6.1 `trace cpu_disasm`, activated by
`:trace :once :file` at natural runtime `$14608` and disabled at `$1473A`, captured
ordered CPU instructions for E/D × `PRINT "A"`/`PRINT 1+2`. The chain and number paths
have 363 and 979 recorded instructions respectively; E and D PC lists match per case.
The Bconout boundary and visible `A`/`3` results are retained. General semantics,
workspace values not printed by the trace and Fwrite selection remain UNMEASURED. See
`analysis/gfa/OUTPUT_TRACE_36.md`, its JSON and `analysis/gfa/P3D2_HANDOFF.md`. P3-C's
scanner/tables remain incomplete.

## Unfinished operations

P3-D/2 is complete with explicit limits. The durable checkpoint is current and attested;
renewal remains disabled by policy. No further scientific operation remains in this
phase.

## Next action

**Clôturer P3-D/2 après vérification automatisée, commit local et finalisation du
checkpoint; conserver le chemin Fwrite comme UNMEASURED.** Preserve all P3-D/2
reports, JSON, tools and raw traces; do not rename TEXT `$5D04`.

## Discoveries not yet incorporated

P3-D/1's candidate-block breakpoint driver (`work/p3d1/run_block_trace.py`) captured the
natural target entry but produced no later ordered block captures before the run ended.
This negative result is retained as instrumentation evidence, not as evidence that the
candidate blocks were not executed. See `OUTPUT_36.md` and `P3D1_HANDOFF.md`.

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
checkpoint-generation: 7
checkpoint-id: g7-0f4e1ab3f156
checkpoint-kind: manual
content-delta: new
readiness: attested
status: checkpoint (guard level 0, remaining ~87877, session 01a1de4d-e170-7336-8945-d268adc65944)
checkpointed: 2026-11-15T08:33:16.089Z
source-goal: cf78d67219ee2fe666f7f42456db99568d8a5ec13609e034ac86771a73edf102
source-progress: e5f5868f47d8c446ff9b1be77ffbca5ad9a36a1be36f990ecf91d096c1824942
source-handoff: c54fdc25f12e5f844aece00f13c050b95756c8741f367fa0a24f22cf1ee02f58
source-learnings: 6d9abfc8f58050c67103f4c6fa8169f6b48f539e52f9eec95015e34e290af7d6
source-config: 37f26ea8df3ae379db57044849c73851c3d7822b1a09fe4b2c2a59f1b4542707


readiness-by: session:01a1de4d-e170-7336-8945-d268adc65944
readiness-at: 2026-11-15T08:33:16.093Z
readiness-checkpoint: g7-0f4e1ab3f156
### Last verified state
guard level 0; checkpoint requested (finalize: P3-D/1 finalized: bounded natural Bconout path reconstructed for PRINT "A" and PRINT 1+2 under E/D; intermediate block order and general semantics remain UNMEASURED. Deliverables committed as 4ed7b76.)

### Unfinished operations
- (none recorded)

### Next action
**P3-D/1 is finished with limits.** Preserve `analysis/gfa/OUTPUT_36.md`,
`OUTPUT_36_DATA.json`, `P3D1_HANDOFF.md` and the partial reconstruction. If continuing,
first obtain reliable natural block-order instrumentation; do not infer missing blocks or
rename TEXT `$5D04`.

### Guard notes
P3-D/1 finalized: bounded natural Bconout path reconstructed for PRINT "A" and PRINT 1+2 under E/D; intermediate block order and general semantics remain UNMEASURED. Deliverables committed as 4ed7b76.
<!-- guard:end checkpoint -->
