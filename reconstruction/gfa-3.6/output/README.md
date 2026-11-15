# P3-D/1 partial output reconstruction

`output.c` is a commented C skeleton of the code statically decoded from the
512-byte capture at runtime `$14608` (TEXT `$5D04`). It preserves the observed
68000 stack conventions and the two output-system call shapes:

- BIOS `Bconout` (#3), character/device pushed before `TRAP #13`;
- GEMDOS `Fwrite` (#64), buffer/count/handle pushed before `TRAP #1`.

Only the Bconout route is dynamically bounded for the accepted natural fixtures:
`PRINT "A"` emits `$41`, and `PRINT 1+2` emits `$33`, both with device `$2`.
The token dispatch, opaque subroutines, positive-format continuation and general
routine name are intentionally not reconstructed.

Evidence: `analysis/gfa/OUTPUT_36.md` and `OUTPUT_36_DATA.json`.
