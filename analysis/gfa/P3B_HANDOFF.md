# P3-B handoff: GFA 3.6 token and text tables

## What is now established

- The constructor at TEXT `$1569E` builds two adjacent workspace word arrays:
  464 words at A6`+$D2C` and 512 words at A6`+$10CC`.
- E and D contain identical static map records and identical constructor and
  selected consumer instruction bytes. Rebuilding both maps yields the same
  1,952-byte SHA-256: `e273593ff6b9e36429c387019b238abcf270408e5070e25671c7e9f88e32e702`.
- Hatari under the same Atari TOS 3.06 TT image captured that exact table hash
  after initialization in both interpreters. A controlled text lookup loaded
  the `PLOT` record; a character lookup loaded the `ASIN(` record. Captures and
  debugger logs are retained under ignored `work/p3b/`.
- The parser candidate at `$12EF6` directly reads the static map at TEXT
  `$1111E`. The two generated workspace maps are read by text/character
  conversion paths. No data flow from those maps to the `$1BEC` handler call
  was established.
- A synthetic dispatcher frame with D6 zero selected first vector target
  TEXT `$869A`; the handler body was not run.
- Four supplied Atari TOS images were inventoried and each boot-probed with its
  matching Hatari machine profile. No local EmuTOS image was found and none was
  downloaded.

## Limits to preserve

The two dynamic inputs were injected into an internal renderer entry point,
not produced by a BASIC parser. The dispatcher frame was also synthetic.
Therefore the operation-level lookup is dynamically demonstrated, but a
natural BASIC tokenization-to-dispatch path remains `UNMEASURED`. A malformed
fixture without the CR terminator overran its bounded input and changed nearby
workspace; it is kept as a failed falsification run and excluded from claims.
Do not treat the table’s inferred spelling role as proof of a complete parser
or interpreter design.

## Suggested P3-C experiment

Create one valid tokenized BASIC input using a known GFA editor/compiler path,
or automate a normal interpreter session with a verified tokenized file. Under
the same TOS 3.06 TT profile:

1. Break at parser entry `$12DF6` and capture the input bytes and any token
   output buffer before execution.
2. Break at the first `$1BD6` reached naturally; capture the A5 frame, D6 and
   selected vector address.
3. Use a one-token statement and a one-character literal, then compare the
   natural values with the static table keys described in
   [TOKEN_TABLES_36.md](TOKEN_TABLES_36.md).
4. Repeat E and D with the same disk, ROM and trace options. Stop before the
   first handler body; retain any run where the parser rejects the fixture as
   a result rather than adjusting bytes until it passes.

If a trustworthy tokenized file is not available, first identify the on-disk
GFA token-file format in the existing distributions. Do not interpret debugger
injections as parser-generated evidence.

## Deliverables and reproducibility

- Analysis: [TOKEN_TABLES_36.md](TOKEN_TABLES_36.md)
- Structured evidence: [TOKEN_TABLES_36_DATA.json](TOKEN_TABLES_36_DATA.json)
- Reconstruction: `reconstruction/gfa-3.6/token-dispatch/`
- Tool and tests: `tools/gfa_token_tables.py`, `tests/test_gfa_token_tables.py`
- Re-run static checks with `make test` and the commands in the main report.
