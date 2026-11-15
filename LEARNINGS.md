# LEARNINGS

## Accepted

- **Address basis:** a TEXT offset is relative to the executable image. In P3-C2 the
  observed TEXT base was `$E904`; therefore TEXT `$5D04` resolved to runtime `$14608`.
  Recalculate from each run's observed base. Evidence: `NATURAL_EXECUTION_36_C2.md`.
- **Measured Hatari profile:** Hatari 2.6.1, Atari TT, Atari TOS 3.06 TT en-GB
  (`work/p3b/roms/tos306-tt-gb.img`, SHA-256
  `974211d0f3db3d81af2d5c564df2e329fec48bb359a8b1eae9edacc9bbda7816`),
  `tools/hatari_gfa_scancode.cfg`. Host X11 symbols were AZERTY although
  `setxkbmap -query` said `us`; verify actual X11 symbols and guest TOS layout separately.
- **Evidence terms:** OBSERVED is direct artifact/runtime evidence; INFERRED is a
  supported interpretation; HYPOTHESIS is falsifiable and provisional; UNMEASURED means
  no result. Keep raw proof under ignored `work/` and cite its hash.
- **Similarity scope:** structural matches do not establish behavioral equivalence.
  Compare only tested behaviors and inputs.
- **Disassembly caution:** `rg-dis` recognizes partial code coverage; annotations and
  `named.veto` labels can be false positives. Confirm control flow/data use independently.
- **Trace attribution:** matching addresses or a nearby dispatcher event do not identify
  a handler. Bind a trace to exact accepted input and selected vector.
- **P3-C3 natural target evidence (accepted, verified this session):** entry-stack return
  word `$104F2` (TEXT+`$1BEE`) proves the natural `JSR (A0)` entry into `$14608`; the
  512-byte target body is byte-identical across all captures and E/D (SHA-256
  `078234b7…`) with a byte-exact reproducible rg-dis 0.11.46 listing; the natural output
  boundary TEXT+`$5E36` (immediately after BIOS `TRAP #13` Bconout, dev=2) is reached in
  all four output runs with the printed character (`$41`/`$33`) and return chain
  `$11070→$14650→$104F2` in the stack capture; screens show `A`/`3` then `OK >` under E
  and D. Dynamic instruction order inside the body remains UNMEASURED; the target is not
  named. Evidence: `analysis/gfa/NATURAL_EXECUTION_36_C3.md`, its DATA JSON.

## Falsified or superseded

- The first `PRINT "A"` keyboard attempt yielded `PRINT 3A3` because host X11 symbols,
  Hatari mapping and guest TOS layout were conflated. Scancode mode plus calibrated
  physical-key events now captures the exact quotes (`22`); deliberate wrong-key tests
  confirm calibration catches errors; buffer bytes, not key events, are the acceptance
  oracle. Evidence: `NATURAL_EXECUTION_36_C2.md`.
- **Single-step of the natural target body (P3-C3):** both methods (`:once :file` entry
  chain and plain `:once` + FIFO commands) failed: Hatari 2.6.1 resumed emulation after
  the `:file` chain and the guest completed the PRINT before the first `hatari-debug c 1`
  (guest `A`/`OK >` echoed in the debugger log; VBL 485→557/619; `cpureg` shows ROM-idle
  loop at `$E00DB8`, A7 supervisor). The 149-step PC lists are the idle interpreter loop,
  NOT the target body. Do not treat them as execution evidence.
  physical-key events now captures the exact quotes (`22`); deliberate wrong-key tests
  confirm calibration catches errors. Evidence: `NATURAL_EXECUTION_36_C2.md`.

## Proposed

- **GOAL.md schema fix (operator action required):** the guard's checkpoint validation
  requires headings `## Objective` and `## Acceptance criteria` in `GOAL.md`; the file
  currently has `## Acceptance` and no `## Objective`. This is a structural heading
  rename only — no semantic change to the objective text. The agent treats GOAL.md as
  operator-owned (protected by project convention). PROGRESS.md headings `## Pending` /
  `## Blockers` were also required and are now present (commit 61e4b8a). The operator
  should apply the GOAL.md rename, then `handoff_finalize` can attest.
- Keep P3-C3 bounded to the immediate natural output path from TEXT `$5D04` for the
  two accepted PRINT cases. Expand only when traces require it.
  (P3-C3 closed on this basis; superseded by completion.)
- **proposed:** to recover ordered execution without dropping into the interactive
  debugger, chain per-instruction `:trace :once :file` breakpoints, or use read
  watchpoints on body format fields during natural continuation.
