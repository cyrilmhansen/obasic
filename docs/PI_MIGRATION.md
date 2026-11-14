# Pi / Handoff migration — H0 qualification

## Qualification

**UNTESTED for task resumption.** The local Handoff runtime loaded in a real Pi 1.5.2
RPC process and answered `/guard status` without inference. This proves module loading and
configuration parsing. It does not prove interactive startup, checkpoint attestation, or
that Pi has resumed P3-C3. No model completion or renewal was run.

## Local audit

| Item | Observed |
|---|---|
| Pi | `pi` at `/usr/bin/pi`, resolves to `/usr/lib/node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js`, version **1.5.2** |
| Node | `v26.12.1` |
| Pi agent directory | `PI_CODING_AGENT_DIR` unset; default `/home/john/.pi/agent` exists |
| Pi packages | `pi list` reported **No packages installed** |
| Extensions/skills before H0 | `~/.pi/agent/extensions` and `skills` absent; no global Handoff installation |
| Project trust | `/home/john/.pi/agent/trust.json` did not list `obasic`; H0 uses explicit `-e` and `--skill` paths, so it does not need to edit global trust |
| Previous obasic Handoff state | No root Handoff docs/config, `.pi-guard`, `.pi-handoff`, or session directory matched `obasic` before H0; no identity or chain was presumed |
| Source used | Local `/home/john/projects/sushiworks/handoff`, source revision `684d8a70e70275273aba5773d1ac0440c323b2d7`; extension banner `0.1.0-rc.1`; source paths were clean at copy time |
| Handoff maturity | Experimental RC for a supervised pilot. The source project documents Pi 1.5.2 zero-inference RPC validation; it does not claim live renewal validation. Pi 1.4.0 is not the installed version |

The installed Pi CLI documents `--extension/-e`, `--skill`, `--mode rpc`, `--offline`,
`--no-session`, `--session-dir` and explicit session selectors. The Handoff installation
instructions are from the local source project's `.agents/skills/pi-handoff/references/bootstrap.md`.
They specify twelve self-contained extension modules, the skill, six durable files,
explicit `recovery.lean` tuning, and verification in Pi itself. H0 copied the extension
and skill into this repo; it did not copy `.pi-guard`, `renewal-state.json`, session
transcripts, identity manifests, attestations, or documents from another project.

## Handoff documents and startup cost

The extension's read-only `recoveryCost` meter returned the following in the diagnostic
Pi session. Its estimator is explicitly **characters / 4**, not billed or exact tokens:

| Tier | Document | Bytes | JS characters | chars/4 estimate |
|---|---|---:|---:|---:|
| Operational (read now) | `HANDOFF.md` | 2,530 | 2,528 | 632 |
| Operational (read now) | `PROGRESS.md` | 1,724 | 1,724 | 431 |
| Methodology (defer) | `AGENTS.md` | 2,526 | 2,524 | 631 |
| Methodology (defer) | `PROTOCOL.md` | 1,304 | 1,304 | 326 |
| Archive (on demand) | `GOAL.md` | 811 | 811 | 203 |
| Archive (on demand) | `LEARNINGS.md` | 1,871 | 1,871 | 468 |
| **Lean operational tier total** | first two docs | **4,254 bytes** | **4,252** | **1,063** |
| **Full six-document set** | all six above | **10,766 bytes** | **10,762** | **2,691** |

The 12,000-token Handoff recovery budget applies to the operational tier; measured
estimate is 1,063. It is not a cap on Pi's model context. Pi automatically discovers
project context files such as `AGENTS.md`; its size is listed above and included in the
full-set estimate. The Handoff lean setting changes the successor's reading order; it
does **not** prevent Pi from auto-loading its context files or change the model window.

`pi --skill .agents/skills/pi-handoff/SKILL.md` makes the skill available. Pi's start
context may include skill metadata or loaded skill text depending on invocation and use;
Handoff's cost meter does not count that, Pi system/tool prompts, or the model's tokenizer.
The skill file is 22,852 bytes / 22,773 JavaScript string code units (about 5,694
chars/4 estimated tokens) if counted in full. A conservative known-content sum of the
lean operational docs, Pi's `AGENTS.md` context and the entire skill would be about 7,388
chars/4 estimated tokens; the full six-doc set plus the entire skill would be about
8,385. These are character estimates, not tokenizer results, and exclude Pi's system
prompt, tool schemas, model metadata and the user's prompt. Thus the known durable content
is below 12,000 by this estimate, while complete initial context remains unmeasured.

**Actual tokens consumed at startup: UNMEASURED.** The zero-inference RPC run had no
selected model (`model: unknown`, context window 0, measurement `unknown / no-model`) and
made no model completion request. `get_state` returned no token usage. This is not a
token-spend measurement; it confirms the diagnostic avoided inference. A real model
session must provide trustworthy provider/Pi usage telemetry before reporting actual
consumption.

Three costs are distinct:

1. **Initial Pi load:** Pi system prompt, tool schemas, project context (including
   `AGENTS.md`), optional skill content and the user's first prompt. H0 has not measured
   its tokenizer total.
2. **Handoff restoration:** a successor gets a recovery instruction. Lean mode tells it
   to read HANDOFF/PROGRESS now, AGENTS/PROTOCOL when needed, and GOAL/LEARNINGS on demand;
   it does not replay the previous transcript.
3. **Renewal:** a guarded state transition creating a successor session. H0 did not
   trigger one, and no obasic renewal chain exists.

## Project installation

H0 vendored the documented 12-module extension in `.pi/extensions/context-guard/` and
the eight-file skill tree in `.agents/skills/pi-handoff/`. No npm package or network
installation was needed. The extension source is the local RC candidate identified
above. `handoff.config.json` opts into lean recovery and a 12,000-character/4 target,
keeps `renewal.enabled` and `renewal.autoRenew` false, and disables documentation cycles.
The existing `AGENTS.md` was preserved as the project-specific operating contract.

No Handoff-managed blocks, mission instance, `.pi-guard` state, checkpoint, attestation
or chain were created by Codex. The first normal Pi session must inspect the live status.
If a checkpoint is still reported missing, Pi/operator may create and attest it using
the documented Pi commands (`/handoff` then `/handoff ready`) after reviewing the prose.
No attestation is represented as present in this repository.

An instance/renewal chain is intentionally not initialized as part of this migration.
The official procedure is `/handoff instance create <id>` in Pi; it creates identity,
empty instance operational docs and one exclusive initial renewal state. If the operator
later elects instance-scoped renewal, Pi must create a fresh id, fill its docs from the
reviewed root docs, then select it with `CONTEXT_GUARD_MISSION_INSTANCE=<id>` or the
config before a new Pi process. Never copy another project's chain or retry initialization
over a partial identity. The present bounded task can run in legacy root-document mode
with renewal disabled.

## First Pi opening

From the repository root, start the interactive TUI with the local extension and skill:

```bash
pi -e .pi/extensions/context-guard/index.ts --skill .agents/skills/pi-handoff/SKILL.md
```

At startup inspect `/guard status`, then call the read-only `handoff_inspect` tool or
operator command `/handoff verify`. Review whether checkpoint state is reported `missing`
or `current`; do not repair or attest anything without reviewing its exact prose. If
missing, use `/handoff` and `/handoff ready` from Pi only. Keep renewal disabled. The
first Pi prompt is deliberately short:

> Follow the unique Next action in HANDOFF.md: P3-C3/1. Begin with the P3-C2 JSON and report, then trace natural `PRINT "A"` and `PRINT 1+2` from TEXT `$5D04` through a bounded output path under E and D. Keep all claims scoped to the captured inputs and stop before reconstructing PRINT generally.

Do not launch P3-C3 until the operator considers the Pi startup and usage display
acceptable. This H0 handoff has not resumed development functionally.

## Evidence and verification

The zero-inference diagnostic ran Pi with explicit extension and skill paths,
`PI_OFFLINE=1`, a temporary isolated `PI_CODING_AGENT_DIR`,
`CONTEXT_GUARD_READONLY=1`, and an external temporary `CONTEXT_GUARD_STATE_DIR`. It
received a structured `/guard status` response with:

- mode `READ-ONLY audit mode`;
- copied extension responding to its registered `/guard status` command (source banner
  inspected as `0.1.0-rc.1`);
- checkpoint missing and renewal disabled/state missing;
- full six-doc estimate 10,762 chars / ~2,691 tokens;
- lean operational estimate 4,252 chars / ~1,063 tokens, below the configured 12,000;
- model/context/usage unknown because no model was selected.

The command ended without inference; temporary agent/state files were removed. It did
not write into the project or initialize a Handoff identity. The local Pi source also
documents `/guard status`, `/handoff verify`, `handoff_inspect` as read-only, `/handoff`
checkpoint and `/handoff ready` attestation. Commands and reports are under
`.agents/skills/pi-handoff/references/commands.md`; bootstrap details are in the source
repo's `references/bootstrap.md`.

H0 files are checked with `make test`, `git diff --check`, JSON parsing, and a real Pi
RPC startup with no model completion. The extension remains an experimental RC; the
live interactive checkpoint/attestation, actual prompt tokens, and first Pi task are
UNTESTED.
