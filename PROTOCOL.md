# Working protocol

- Read `AGENTS.md` first. Preserve its project contract and all operator changes.
- Keep originals, ROMs, generated disassemblies and raw traces under `work/`; never
modify them. Do not fetch historical software without a documented need.
- For every claim record exact artifact, SHA-256, tool/version, address basis and
evidence path. Distinguish OBSERVED, INFERRED, HYPOTHESIS and UNMEASURED.
- A TEXT offset is not an absolute address. Record the observed load base and calculate
runtime addresses for each run.
- Structural correspondence does not prove behavioral equivalence. Separate E and D
measurements and do not extend a conclusion beyond tested inputs.
- Treat `rg-dis` annotations and `named.veto` regions as candidates until independently
checked against control flow or data references.
- Use isolated emulator homes/disks; capture actual inputs and outputs. Do not use a
debugger to fabricate the state being claimed as natural execution.
- Commit only task deliverables with explicit paths. Never push automatically; preserve
pre-existing work and do not use `git reset`, `git clean` or `git add -A`.
- Verify code changes with `make test` and `git diff --check`. Pi Handoff checkpoints
and attestations are performed in a Pi session, never manufactured by an agent.
