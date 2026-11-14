# P3-A handoff: GFA 3.6 startup

## Completed

The GEMDOS entry route for the 3.6 E and 3.6TT D interpreters is mapped from TEXT `$0000` through the token-dispatch boundary at `$1BD6`. The direct startup path reaches `$0026`, then jumps to `$181C`; the matched 322-instruction P2 span is not a proven function. Selected initialization routines are reconstructed in [startup.c](../../reconstruction/gfa-3.6/startup/startup.c), with evidence and uncertainty in [STARTUP_36.md](STARTUP_36.md) and machine-readable measures in [STARTUP_36_DATA.json](STARTUP_36_DATA.json).

The bounded E/D comparison has 252 instruction rows, 86/86 statically resolved direct control transfers agreeing, and one unresolved indirect jump. The four changed operand sites are two relocated BSS pointers and two localized error-string references. The referenced jump table agrees at 26/26 entries and the VDI/AES offset table at 22/22. This supports a shared startup implementation, not behavioral equivalence.

## Recommended P3-B: parser lookup tables and token dispatch

Start with the table builder at TEXT `$1569E`, reached during initialization. It clears a region at workspace `$D2C` and fills tables at `$D2C` and `$10CC` from static maps at `$11EDB` and `$1111E`. These operations are observed; “token/parser table” is an inference from shape and its startup call path. Follow all reads and writes to those destinations, then connect the tables to parser candidate `$12DF6` and the handler table used at `$1BEC`.

Suggested bounded questions:

1. What exact byte/word layout and index domain do the two generated tables have?
2. Which parser/dispatcher instructions consume each table, and what token classes do they select?
3. Are the table layouts and consumers exact or relocated between E and D?
4. Can a synthetic byte/token fixture falsify the inferred mapping without requiring full BASIC execution?

This work is separable from completing helper semantics at `$A424`, `$A632`, `$8D6C`, and `$E264`. It has an observed startup dependency and static maps available, so it is the strongest next reconstruction lot.

## Alternative: command-tail and interactive input

The command-tail reader at `$1924..$1974` is short and visible, but its NUL-termination assumptions and later command path need dynamic validation. Hatari 2.6.1 is present; no local TOS ROM was found. Do not download one automatically. With an authorized ROM, run both PRGs under a recorded TT profile and compare zero-length, ordinary, maximum-length, and boundary-tail cases. Preserve ROM hash, emulator options, PRG hash, and trap/memory trace.

The prompt loop reaches parser `$12DF6`; do not expand P3-B into reconstructing the parser unless the table trace makes that a deliberate next phase.
