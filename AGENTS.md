# obasic — agent operating contract

**Goal:** traceable historical reconstruction first; modern, maintainable implementation second. Byte-exact code generation is not required.

## Hard boundaries

- NEVER invent a binary, tool output, machine address, routine name, emulator observation, or version label.
- Keep original binary bytes, rg-dis generated listings, and third-party source in ignored `work/`, never commit or publish them without a documented rights review.
- Use pinned tool versions and SHA-256. Cite exact artifacts and locations in each claim.
- Distinguish **OBSERVED**, **INFERRED**, **HYPOTHESIS**, and **UNMEASURED**.
- Run experiments that could falsify the hypothesis; record failures as first-class evidence.
- Do not silently patch or annotate a generated listing; keep original output immutable and write separate overlays in `analysis/<target>/`.
- Never treat rg-dis GFA runtime annotations as evidence of the original interpreter's implementation without a control-flow check. False positives are possible.
- Do not mistake 6502 for 68000, source tokens for executable instructions, or a floppy image for a single executable.
- Do not run commands against unrelated repositories, edit operator configuration, or push to a remote automatically.

## Agent responsibilities

**Archaeologist (Sushi/Qwen):** inventory signatures, follow call graphs, suggest hypotheses, prepare annotated routine descriptions, list necessary discriminating tests. Supply evidence addresses and artifact IDs.

**Verifier (Codex):** independently validate the claims, execute emulator experiments when available, reproduce hashes and disassembly commands, reject weak inferences.

**Modern engineer (Codex):** implement clean semantic components and regression tests; never modify historical annotations to make new code pass.

## Deliverable format

For each subsystem, create `analysis/<target>/<area>.md` with:

1. Research question and binary SHA-256.
2. Relevant source artifact, instruction ranges and tool version.
3. Findings tagged OBSERVED / INFERRED / HYPOTHESIS / UNMEASURED.
4. At least one falsification experiment (or reason impossible).
5. Reproducible command, exit status, evidence filenames.
6. Open questions / next handoff.

A reconstruction is not 'done' merely because it reads well; it needs independently checked behavior, or an explicit unmeasured label.
