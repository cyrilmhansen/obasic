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

## Falsified / corrected

- The first `PRINT "A"` keyboard attempt yielded `PRINT 3A3` because host X11 symbols,
  Hatari mapping and guest TOS layout were conflated. Scancode mode plus calibrated
  physical-key events now captures the exact quotes (`22`); deliberate wrong-key tests
  confirm calibration catches errors. Evidence: `NATURAL_EXECUTION_36_C2.md`.

## Proposed

- Keep P3-C3 bounded to the immediate natural output path from TEXT `$5D04` for the
  two accepted PRINT cases. Expand only when traces require it.
