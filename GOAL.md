## Objective
# Project goal

Build a traceable historical reconstruction of GFA BASIC interpreters, runtimes and
compilers, starting from preserved binaries and independently checked observations.
Keep claims tied to exact artifacts; reconstruction is partial where evidence ends.

## Acceptance criteria

- Reproducible measurements and historical addresses accompany each claim.
- Findings distinguish OBSERVED, INFERRED, HYPOTHESIS and UNMEASURED.
- Static similarity is never presented as behavioral equivalence.
- Original binaries, ROMs, raw listings and traces remain under ignored `work/`.

Current bounded development objective: trace the natural `PRINT "A"` and `PRINT 1+2`
paths from their P3-C2 evidence through the selected TEXT `$5D04` target and identify
only the immediate output dependencies demonstrated by traces.
