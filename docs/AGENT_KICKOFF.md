# Initial agent briefs

## Archaeologist — first task

Study AGENTS.md and docs/SCIENTIFIC_PROTOCOL.md. Inventory all known Turbo-BASIC XL 1.5 and GFA 1.0, 2.02, 3.02, 3.60, 3.6TT interpreter/compiler/run-only/runtime artifacts. For each verified binary provide origin, filename, size, SHA256, claimed version and strength of attribution. Do not invent missing binary or version information. For Turbo-BASIC XL investigate dmsc/turbo-dis as a third-party annotated reference, not as the original historical source. For GFA, only use rg-dis against actual extracted 68000 executables and store full outputs in ignored work/. Produce a factual source inventory and list major gaps. Do not write a modern compiler yet.

## Verifier — first task

Check the archaeological inventory independently. Confirm every executable actually corresponds to the asserted target and role. Check tool version and exit codes from receipt.json; rerun a sampled inspection. On GFA v2/v3, compare rg-dis with and without GFA annotations; classify inferred function names as probable until verified. On GFA v1, do not assume known library signatures. Report falsifiable disagreements.

## Modern engineer — first task (after evidence exists)

Choose one vertical slice in the interpreter (tokens -> expression evaluation -> result), document observed contracts and limits, build an independently testable implementation. Do not derive behavior solely from a decompiler name or assume compiler/interpreter semantics are identical.
