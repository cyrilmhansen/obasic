# GFA BASIC compiler 3.6 TT D/E structural comparison

## Question and sources

Do the GFA BASIC 3.6 TT D and E compiler PRGs share an implementation, and where are their structural differences?

| Item | Revision E | Revision D |
|---|---|---|
| Source image | `work/disks/GFA Basic v3.6 (1991-05-06)(GFA Systemtechnik).st` | `work/disks/gfa_basic_3_6tt_gfa_systemtechnik.ST` |
| Image SHA-256 | `ed98931c7b57b501c3dbe3f14704d0bdf1ef75e2bca8f35554d34455e4dda842` | `5f1652b68833b1f75666f4f6a5920bb0389db3a8ae986dcaed8100bb9a0b5615` |
| Extracted member | `COMPILER/GFA_BCOM.PRG` | `GFA_BCOM.PRG` |
| PRG bytes | 73,070 | 73,091 |
| PRG SHA-256 | `a2ffa32cdf46079821721dd22b9284c446d944492bd242f661f96ab5d69991bc` | `47b4527a00656d840ab4a76ccba2e718cbd6e7abe162b6da75167cd1344290e8` |

The executable hashes above are of the extracted PRGs, not the floppy images. Reproducibly extract them with `tools/extract_st_member.py`; extracted bytes remain under ignored `work/`.

**OBSERVED — executable layout:** the GEMDOS headers report text/data/BSS sizes of E `65,046/7,284/18,662` and D `65,062/7,290/18,662` bytes. Both have zero symbol bytes and relocations. `rg-dis` reports 532 relocation entries for each PRG. The relocation stream occupies 712 bytes in E and 711 in D. The BSS is byte-for-byte equal in size; D has 16 more text bytes and 6 more data bytes.

**OBSERVED — decoder summary:** `rg-dis` 0.11.46 reports 6,023 instructions and 18,068 covered instruction bytes for each executable, minimum CPU 68000, no non-68000 instructions and no FPU requirement. The counts match the existing image-based records `work/rg/compilers/metadata/gfa-bcom-36.json` and `gfa-bcom-36tt.json`, and were reproduced from the extracted PRGs in `work/rg/compilers/36de-structural/36E.inspect.json` and `36D.inspect.json`.

## Method and coverage

The new reusable comparator is `tools/structural_compare.py`. It compares strict executable bytes, aligns decoded instructions from offset-annotated `rg-dis` listings, retains numeric constants, and then checks whether local branch destinations follow the instruction mapping. The test/report listings disable GFA annotations and smart labels. The primary instruction alignment also excludes regions tagged `named.veto`; the project protocol warns that named GFA regions can be false positives. These regions remain explicit ambiguity rather than being treated as confirmed code.

The instruction denominators below are intentionally separate:

| Measure | E | D |
|---|---:|---:|
| `rg-dis` summary instructions | 6,023 | 6,023 |
| Candidate instruction rows in primary comparison (outside `named.veto`) | 5,283 | 5,474 |
| Candidate rows paired after address normalization | 4,929 | 4,929 |
| Paired rows with identical mnemonic and operands | 3,330 | 3,330 |
| Candidate-row pairing coverage | 93.299% | 90.044% |
| Coverage against `rg-dis` 6,023-instruction denominator | 81.84% | 81.84% |

Among paired rows, the other 1,599 operand spellings differ only in `_Lxxxx` address labels. After normalizing those references, **zero** paired rows have a remaining operand difference. In particular, the comparator does not erase immediate constants. This supports shared code structure in the compared subset, but it is not evidence that every byte or every recognized instruction is equivalent.

**OBSERVED — exact bytes:** at the same file offsets, 10,575 bytes (14.472% of the smaller PRG) match across the full files; 7,341 bytes (11.286% of the smaller text section) match at the same text offsets. Sequence matching finds 71,469 exact byte pairs across the PRGs and 63,467 within text, with a longest exact text run of 4,901 bytes. These latter figures count exact byte runs after shifts; they are an alignment measure, not byte-for-byte equality of the files.

**OBSERVED — instruction blocks:** the primary alignment has 201 contiguous matching instruction blocks; the longest contains 523 candidate instructions. Representative high-confidence blocks (offsets are relative to PRG load address `$10000`) are:

| E start → D start | Matched instructions |
|---|---:|
| `$135C8` → `$135D8` | 523 |
| `$168D0` → `$168E0` | 490 |
| `$1D064` → `$1D074` | 467 |
| `$159A0` → `$159B0` | 416 |
| `$16480` → `$16490` | 270 |
| `$1D806` → `$1D816` | 141 |

These long blocks, the 4,929 paired candidate instructions, and the address-only operand differences are strong evidence that D and E share a substantial code base. Block confidence is high where long exact instruction sequences align and their resolved local branches preserve the mapping.

`rg-dis --inspect functions` reports 57 inferred function spans for each PRG. Function boundaries are not independently validated. With the primary region mask and strict overlap/coverage scoring, 4 function-span pairs meet the tool's high-confidence threshold and 3 meet its medium threshold; this is a conservative lower bound, not a claim that the other routines differ. The JSON contains the pair scores and synthetic labels. It does not assign historical routine names.

**OBSERVED — control flow:** among paired candidate branches with local labels, 1,014 of 1,014 resolved target checks land on the corresponding mapped instruction. Another 586 branch checks do not have a resolvable local target in this format and remain unmeasured. Candidate rows left unpaired are 354 for E and 545 for D; these are not automatically semantic changes because insertions and ambiguous regions can break sequence alignment.

## Differences observed

**OBSERVED — revision marker:** at text offset `$00000E` (load address `$1000E`) the embedded startup string says `GFA-BASIC Compiler 3.6 TT E` in E and `... D` in D. The string uses equal length, so the following code begins at the same offset.

**OBSERVED — diagnostic text:** E contains `Variable type mismatch` at text offset `$02BD6` (file offset `$02BF2`); D contains `Falscher Variablentyp` at text offset `$02BE8` (file offset `$02C04`). The associated local branch shown at E `$12C60` and D `$12C70` selects the corresponding message path. This is a concrete text/data difference and a 16-byte layout shift at that location; its user-facing context is consistent with English versus German diagnostics.

**OBSERVED — layout and relocation positions:** both files contain 532 relocation entries, but only 48 relocation offsets are identical; 484 offsets occur at different positions in each file. This is consistent with shifted code/data layout and does not by itself establish 484 changed absolute references. The header and relocation-stream length explain why full-file byte equality is much lower than aligned code similarity.

**INFERRED:** the revisions share a common compiler implementation with localized diagnostic data and small layout changes. The equal instruction count is not the basis for this inference; it follows from byte and instruction alignment plus the resolved branch checks.

**HYPOTHESIS:** the observed English/German diagnostic difference reflects a language/localization build choice, while most remaining layout differences come from inserted or resized code/data early in the image. A further matched data-string inventory and execution tests could falsify this.

**UNMEASURED:** behavior of the two compiler executables on identical BASIC inputs has not been tested in an Atari emulator. This report makes no claim that generated machine code or error behavior is equivalent.

## Regions not analyzed as confirmed code

`rg-dis --inspect regions --record-decisions` divides each text+data image as follows:

| Region kind | E bytes | D bytes |
|---|---:|---:|
| Code-classified ranges (all rules) | 58,566 | 58,606 |
| Of which `named.veto` heuristic ranges | 42,068 | 41,560 |
| Data | 13,232 | 13,236 |
| String | 392 | 355 |
| Unknown/undecodable | 140 | 155 |
| BSS | 18,662 | 18,662 |

The `named.veto` byte ranges are excluded from the primary comparison. The 140/155 unknown bytes are likewise not instruction evidence. These facts and full per-range decisions are in `36E.regions.json` and `36D.regions.json` under `work/rg/compilers/36de-structural/`. The source `rg-dis` listings are machine output; their classification is not an independent proof of original control flow.

## Falsification and reproducibility

Four synthetic tests in `tests/test_structural_compare.py` check that the comparator:

1. pairs code after an insertion and follows a relocated branch target;
2. leaves a changed immediate constant unmatched instead of normalizing it away;
3. reports a changed control-flow target even when the branch instruction otherwise aligns;
4. preserves an inserted instruction as unpaired.

The tests passed as part of the full repository test run: `make test`, exit status 0 (13 tests). This falsifies the unsafe hypothesis that every same-mnemonic instruction or equal instruction count means equivalence.

Reproduction commands (all completed with exit status 0):

```sh
python tools/extract_st_member.py 'work/disks/GFA Basic v3.6 (1991-05-06)(GFA Systemtechnik).st' COMPILER/GFA_BCOM.PRG work/extracted/gfa-compiler-36de/36E.PRG
python tools/extract_st_member.py work/disks/gfa_basic_3_6tt_gfa_systemtechnik.ST GFA_BCOM.PRG work/extracted/gfa-compiler-36de/36D.PRG
rg-dis work/extracted/gfa-compiler-36de/36E.PRG --arch 68k --cpu auto --machine st --quiet --no-annotate-gfa --no-smart-labels --annotate-offsets -o work/rg/compilers/36de-structural/36E.normalized.s
rg-dis work/extracted/gfa-compiler-36de/36D.PRG --arch 68k --cpu auto --machine tt --quiet --no-annotate-gfa --no-smart-labels --annotate-offsets -o work/rg/compilers/36de-structural/36D.normalized.s
rg-dis work/extracted/gfa-compiler-36de/36E.PRG --arch 68k --machine st --quiet --json --inspect regions --record-decisions > work/rg/compilers/36de-structural/36E.regions.json
rg-dis work/extracted/gfa-compiler-36de/36D.PRG --arch 68k --machine tt --quiet --json --inspect regions --record-decisions > work/rg/compilers/36de-structural/36D.regions.json
rg-dis work/extracted/gfa-compiler-36de/36E.PRG --arch 68k --machine st --quiet --json --inspect functions > work/rg/compilers/36de-structural/36E.functions.json
rg-dis work/extracted/gfa-compiler-36de/36D.PRG --arch 68k --machine tt --quiet --json --inspect functions > work/rg/compilers/36de-structural/36D.functions.json
python tools/structural_compare.py work/extracted/gfa-compiler-36de/36E.PRG work/extracted/gfa-compiler-36de/36D.PRG work/rg/compilers/36de-structural/36E.normalized.s work/rg/compilers/36de-structural/36D.normalized.s --left-regions work/rg/compilers/36de-structural/36E.regions.json --right-regions work/rg/compilers/36de-structural/36D.regions.json --left-functions work/rg/compilers/36de-structural/36E.functions.json --right-functions work/rg/compilers/36de-structural/36D.functions.json --json work/rg/compilers/36de-structural/compare.json
make test
```

Tool pin evidence: `rg-dis 0.11.46`, executable SHA-256 `1a66448a2a3215ded9e89515f3e0c5fbb02e7d05ec9e8bc175dda492734bc4ef`. Machine evidence and detailed pair maps are intentionally ignored under `work/rg/compilers/36de-structural/`; the comparator, extractor, tests, and this report are tracked project artifacts.

## Open questions / next handoff

- Run both compilers under a pinned Atari ST/TT emulator with identical valid and invalid BASIC inputs; compare output bytes and diagnostics.
- Review the 1,599 shifted-label operand pairs in context and the 586 unresolved branch forms.
- Independently validate `rg-dis` function boundaries before naming or assigning responsibilities to routines.
- Compare all differing strings and the non-`named.veto` unpaired instruction clusters, preserving byte offsets and not treating data-table shifts as code changes.
