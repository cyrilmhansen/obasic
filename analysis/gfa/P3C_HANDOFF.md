# P3-C handoff — parser/dispatcher natural-input attempt

## Result

The requested positive oracle was **not obtained**. Both interpreters were run in Hatari 2.6.1 under the same Atari TOS 3.06 TT ROM, and both reached the interactive parser entry after keyboard input. The bytes captured at the parser were `PRINT 3A3` followed by CR, not the intended `PRINT "A"`; both versions rejected the input with their localized syntax message. No valid statement or expected output was demonstrated.

One D run reached dispatcher `$1BD6` and the indirect call at `$1BEC`, resolving `A0=$14608`. Because the entry text was invalid and the debugger did not bind this capture to a specific accepted statement, treat it as a dispatcher-boundary observation with **ambiguous input association**, not as the requested parser-to-handler proof. E dispatcher selection remains unmeasured. No natural reads of `$D2C`, `$10CC`, or static `$1111E` were confirmed.

## Evidence and reproducibility

Read [NATURAL_EXECUTION_36.md](NATURAL_EXECUTION_36.md) and [NATURAL_EXECUTION_36_DATA.json](NATURAL_EXECUTION_36_DATA.json) for hashes, exact registers, addresses, per-file checksums, coverage, and limits. Original PRGs and the ROM were not edited. Raw Hatari traces, screenshots, debugger scripts, and isolated disks remain under ignored `work/p3c/`.

The E and D TEXT base observed in Hatari was `$E904`; therefore the dynamic parser breakpoint address was `$216FA`, not the offset `$12DF6`. The internal scanner point `$12EF6` is distinct from this prompt-called entry. Its static reference to `$1111E` is known from P3-B, but was not dynamically confirmed in these runs.

## Next discriminating experiment

Before another parser trace, determine the guest keyboard mapping. Use a small calibration session that types one character at a time in GFA direct mode and captures parser A0 bytes, covering quote, digits, plus, space, and CR. Do not interpret X11 text as guest text until its emitted bytes match. Then enter `PRINT "A"` and `PRINT 1+2`, verify the exact bytes at parser entry, and only then arm separate read watchpoints for `$1111E`, A6`+$D2C`, A6`+$10CC`, `$1BD6`, and `$1BEC`. Repeat independently with E and D on reset emulator state.

If normal keyboard calibration remains unreliable, save a minimal line using the historical editor and verify the resulting file bytes, hash, and normal reload before tracing it. Do not convert an arbitrary text file into a presumed tokenized source.

## P3-D scope recommendation

Do not start a broader P3-D handler reconstruction yet. First close the P3-C positive path through a valid natural `PRINT` statement and its first handler. Once that succeeds, P3-D can be bounded to the output handler and its string or numeric formatting path reached by these two statements. Keep the table renderer paths from P3-B as a separate candidate unless natural watchpoints show they are used by `PRINT`.
