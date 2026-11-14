# GFA BASIC lineage: comparative map

## Question and scope

This study asks whether the available GFA BASIC 1.0, 2.02, 3.02, 3.6 and 3.6TT interpreter, run-only and compiler binaries share detectable code structure. It maps candidate continuity; it does not reconstruct source or establish behavioral equivalence.

**OBSERVED:** the five available disk images and 47 active directory members selected for executable/object inspection are catalogued, with image and extracted-member SHA-256, in [INVENTORY.md](INVENTORY.md) and [LINEAGE_DATA.json](LINEAGE_DATA.json). The inventory gives member-file sizes and hashes; embedded-string and comparator positions are `rg-dis` listing offsets, and comparator function spans are TEXT-relative (not relocated runtime addresses). The 3.02-labelled disk contains multiple generations: `GFABASV3.PRG` identifies itself as 3.02; its `GFABASIC.PRG` and `GFABASRO.PRG` identify as version 2.0. Support label, executable identity, and internal version are therefore kept separate.

## Method and denominators

The pinned decoder is `rg-dis` 0.11.46, SHA-256 `1a66448a2a3215ded9e89515f3e0c5fbb02e7d05ec9e8bc175dda492734bc4ef`. The lineage listings were generated for 68k with GFA annotations and smart labels disabled, and offsets annotated. Comparisons reuse `tools/structural_compare.py` and its P1 matching rules unchanged. The P1 D/E comparison is included as a control. Full commands, source paths, extraction notes, hashes, section/relocation details, decoder summaries and comparison JSON are recorded in `LINEAGE_DATA.json` and ignored `work/rg/p2-lineage/` evidence.

A comparator denominator is the number of candidate instruction rows after its region filtering, not the `rg-dis` CPU instruction total. `named.veto` and unknown ranges are excluded from candidate rows. A pair can be exact, or normalized as a reference-only change; numeric constants are not normalized. `aligned_exact_bytes` is an alignment statistic, not a measure of semantic equivalence. Function spans are confidence-scored structural candidates; labels are not functional names. Branch checks count only resolvable candidate branches, with unresolved references reported separately.

### Interpreter lineage

| Pair (identified executable) | Candidate rows L/R | Paired; exact | Coverage L/R | Branches matching / verifiable; unresolved | Function spans high / medium | Assessment |
|---|---:|---:|---:|---:|---:|---|
| 1.0 `GFABASIC` → 2.02 `GFABASIC` | 2,601 / 3,794 | 1,413; 980 | 54.325% / 37.243% | 219 / 221; 212 | 0 / 5 | Partial |
| 2.02 `GFABASIC` → 3.02 `GFABASV3` | 3,794 / 2,744 | 246; 159 | 6.484% / 8.965% | 40 / 40; 47 | 0 / 0 | Indeterminate |
| 3.02 `GFABASV3` → 3.6 `GFABASIC` | 2,744 / 4,329 | 2,006; 1,440 | 73.105% / 46.339% | 387 / 389; 178 | 4 / 9 | Partial |
| 3.6 `GFABASIC` → 3.6TT `GFABASIC` | 4,329 / 4,355 | 4,327; 4,324 | 99.954% / 99.357% | 920 / 920; 295 | 22 / 12 | Strong |

The key 2.02 → 3.02 transition is indeterminate because the main 3.02 executable has only 8.965% paired candidate coverage. The 3.02 disk's legacy `GFABASIC.PRG`, internally marked “GFA BASIC V 2.0 US” at offset `$CE48`, produces a different, misleadingly stronger comparison with 2.02: 2,443/3,794 pairs, 1,669 exact (64.391% / 86.386% coverage), 434/435 verifiable branches matching, and 349 unresolved. This is evidence for a 2.0 lineage copy on the disk, not for the 3.02 main interpreter.

**OBSERVED:** 3.6 and 3.6TT interpreter full PRGs share 102,429 bytes in exact sequence alignment (longest run 16,644); 92,794 bytes match at the same file offsets. Among candidate rows, there are 3 operand differences and all are address-reference-only; 28 3.6TT rows and 2 3.6 rows are unpaired. The matched control flow is consistent at all 920 verifiable branches. This supports strong structural continuity, not identical binaries or behavior. For address anchors, a high-confidence 3.02/3.6 span pair is 105 instructions across listing offsets `$13E68`–`$1407E` and `$14FA6`–`$151BC`. The top 3.6/3.6TT candidate spans include 322 instructions at `$0000`–`$0306` in each listing and 197 at `$8D6C`–`$8FE0` in each. These are structural anchors, not behavioral labels. In 3.6/3.6TT, unpaired candidate rows include 3.6 offset `$8EB4` and 3.6TT offsets `$8EB4`, `$165BA`, `$170AE`; the full unpaired address lists and block map are in `work/rg/p2-lineage/comparisons/interpreter-3.60_to_3.6TT.json`.

**INFERRED:** the 3.02 main interpreter and 3.6 interpreter retain a partial common code base: 2,006 candidate pairs, including 1,440 byte/opcode-and-operand exact pairs and 565 reference-only changes. But 738 left and 2,323 right candidate rows remain unmatched (addresses are in the comparison JSON); low same-offset bytes (4.503% of the smaller TEXT) show substantial relocation/reorganization, and no behavior is established. There is one changed non-reference operand among the 566 changed pairs. The four high-confidence and nine medium-confidence function-span pairs are evidence for local structural continuity only.

### Runtime and interpreter/runtime comparisons

| Pair | Candidate rows L/R | Paired; exact | Coverage L/R | Verifiable branches matched | Assessment |
|---|---:|---:|---:|---:|---|
| 1.0 run-only → 2.02 run-only | 2,100 / 2,604 | 1,353; 934 | 64.429% / 51.959% | 232 / 233 | Partial |
| 2.02 run-only → 3.02 disk `GFABASRO` (internal 2.0) | 2,604 / 2,443 | 2,187; 1,563 | 83.986% / 89.521% | 403 / 404 | Strong structural continuity |
| 3.02 disk `GFABASRO` (2.0) → 3.6TT run-only (3.5) | 2,443 / 3,555 | 51; 42 | 2.088% / 1.435% | 4 / 6 | Indeterminate |
| 1.0 interpreter ↔ run-only | 2,601 / 2,100 | 1,804; 1,243 | 69.358% / 85.905% | 300 / 300 | Partial shared structure |
| 2.02 interpreter ↔ run-only | 3,794 / 2,604 | 1,902; 1,329 | 50.132% / 73.041% | 340 / 340 | Partial shared structure |
| 3.02 legacy 2.0 interpreter ↔ run-only 2.0 | 2,828 / 2,443 | 1,756; 1,217 | 62.093% / 71.879% | 312 / 314 | Partial shared structure |
| 3.6TT interpreter ↔ run-only 3.5 | 4,355 / 3,555 | 2,302; 1,703 | 52.859% / 64.754% | 438 / 439 | Partial shared structure |

The cross-generation runtime 2.02 → disk 3.02 run-only result compares two executables both internally marked version 2.0/2.02, not a confirmed 3.02 runtime. The 3.02 V3 candidate versus run-only 2.0 is also weak: 85 pairs of 2,744/2,443 rows (3.098% / 3.479%), 10 of 12 branches matching, 14 unresolved. No runtime for a confirmed 3.02 V3 build was identified. Runtime-to-interpreter overlap is expected for shared facilities, but does not by itself identify a runtime interface or prove the run-only file was generated from the interpreter.

### Compiler lineage

| Pair | Candidate rows L/R | Paired; exact | Coverage L/R | Branches matching / verifiable; unresolved | Assessment |
|---|---:|---:|---:|---:|---|
| 3.6 compiler E → 3.6TT compiler D (P1 control) | 5,283 / 5,474 | 4,929; 3,330 | 93.299% / 90.044% | 1,014 / 1,014; 586 | Strong structural continuity |
| 2.02 `GFACOM17` → 3.6 compiler E | 5,306 / 5,283 | 34; 21 | 0.641% / 0.644% | 0 / 0; 13 unresolved | Indeterminate |
| 2.02 `GFACOM17` → 3.6TT compiler D | 5,306 / 5,474 | 35; 22 | 0.660% / 0.639% | 0 / 0; 13 unresolved | Indeterminate |

The two packaged `GFACOM17.PRG` copies are exact duplicates. The separate `rg-dis --inspect cpu` summary reports zero covered bytes for GFACOM17, while the recorded forced-68k assembly listing does contain decoded rows. The structural comparison pairs only 34/5,306 or 35/5,306 candidate rows; no branches resolve and no high-confidence spans exist. This conflict between inspect and forced-architecture views, plus the tiny pairing, leaves compiler lineage indeterminate. Its relation to the later compiler is **INDETERMINATE**. P1 established that E/D compiler pairs comprise 3,330 exact instruction rows and 1,599 reference-only operand differences, with every one of 1,014 verifiable local branch checks matching. It did not prove output or behavioral equivalence.

## Architectural work map

This section names evidence classes, not reconstructed routines.

- **OBSERVED — TOS startup/environment candidates:** entry blocks at TEXT offset `$0000` are medium-confidence matched in the 1.0→2.02 comparison (149 instruction pairs) and high-confidence matched in 3.6→3.6TT (322 pairs). Nearby code references basepage fields and GEMDOS calls such as `Mshrink`/`Malloc` in the disassemblies. This supports an initialization/environment family. The routine's full historical purpose remains unverified.
- **OBSERVED — local 3.02/3.6 and 3.6/TT structure:** four high plus nine medium spans match 3.02 V3→3.6; 22 high plus 12 medium spans match 3.6→3.6TT. Their synthetic labels and byte spans are catalogued in comparison JSON. No span is assigned a syntax, expression, variable, string, numeric, control-flow, or I/O name from shape alone.
- **OBSERVED — version/runtime strings:** internal release markers distinguish main interpreter and run-only roles, including 3.02 V3 (`$E1E9`, `$15D66`), legacy 2.0 (`$CE48`), 3.6TT 3.5 run-only (`$CEDC`), and compiler E/D markers (`$000E`). Strings identify artifacts and diagnostics; they do not prove which routine emits them.
- **INFERRED — 3.6/TT shared compiler/library ecosystem:** 3.6 and 3.6TT have three exact executable duplicates (`MAKE_NDX`, `DEF2DFN`, `RCS2`) and the compiler libraries have large sequence-level byte overlap. The library format and runtime role remain unknown.
- **UNMEASURED:** parser/token dispatch, expression evaluation, variable/array and string managers, math, error paths, I/O, and compiler/runtime interfaces have not been semantically mapped. Emulator-based differential probes were not run.

## Sections, data and unresolved coverage

TOS PRGs expose TEXT/DATA/BSS and relocation counts in the inventory. Principal interpreter and compiler section values are listed per binary there; the 3.6/TT interpreter text grows from 102,288 to 102,460 bytes while both report DATA 36, BSS 1,088, and 2,024 relocations. Compiler E/D text is 65,046/65,062; DATA 7,284/7,290; BSS both 18,662; relocations both 532. These are layout observations, not semantic data-table matches.

`rg-dis` marks recognized code versus data/veto/unclassified regions. CPU instruction counts are not full TEXT coverage: e.g. the 3.6 interpreter has 8,582 recognized instructions covering 25,932 bytes in a 102,288-byte TEXT. The structural comparator filters candidate rows further. Exact excluded counts and row offsets can be read from raw JSON/listings under `work/rg/p2-lineage/`; unknown, vetoed and unpaired bytes remain unresolved. Any lack of a match may reflect missed decoding, transformed code, or comparator limits; it is not proof of a rewrite.

The 3.02 disk's `GFABASIC.PRG` directory size claims 64,320 bytes while its FAT chain yields 56,320. Strict extraction fails. The recovery path validates the GEMDOS header and complete relocation terminator, then extracts 56,128 bytes without inventing the missing 8,000 bytes. Inventory notes include the evidence and extraction command. The recovered file's observed internal version string makes clear it is a legacy 2.0 US executable rather than the 3.02 main program.

Exact cross-image duplicates: 3.6/3.6TT `MAKE_NDX` (1,420 bytes), `DEF2DFN` (13,971 bytes), `RCS2` (96,083 bytes); and `C_TST.O` (116 bytes, DRI object, not standalone executable). The two 2.02 copies each of `GFABASIC`, `GFACOM17` and `ASSEM` are also exact duplicates. `ASSEM.BAK` copies are equal but invalid as complete PRGs. Full hashes are catalogued in JSON.

## Falsification and reproducibility

**OBSERVED:** synthetic comparator tests cover inserted code, relocated branch targets, changed constants, control-flow changes, and old short `$0000` offset annotations. Extraction tests cover a complete relocation-terminated recovery, zero relocation marker, and failure on unterminated relocation data. P1's exact D/E result was rerun after the parser compatibility update and reproduced: 4,929/5,283 vs 5,474 candidate rows paired, 3,330 exact, 1,599 address-only changes, 0 other operand changes, and 1,014/1,014 verifiable branch checks.

Reproduce the required suite from the repository root with `make test`, then `git diff --check`. For any executable, regenerate its listing with `rg-dis FILE --arch 68k --machine st (or tt) --quiet --no-annotate-gfa --no-smart-labels --annotate-offsets -o LISTING.s`; the receipt paths and executable hashes are in `LINEAGE_DATA.json`. Re-run a pair with `python3 tools/structural_compare.py LEFT.prg RIGHT.prg LEFT.s RIGHT.s --left-regions LEFT.regions.json --right-regions RIGHT.regions.json --left-functions LEFT.functions.json --right-functions RIGHT.functions.json --json OUT.json`. The exact raw comparison report for every normalized result is linked by its `evidence` field in `LINEAGE_DATA.json`. Retain large disassemblies and extracted historical members only in ignored `work/`. No network retrieval was used. No original image, extracted historical executable in source control, or raw listing was modified.

## Relationship decision

| Family | Current conclusion | Confidence |
|---|---|---|
| Main interpreter 1.0→2.02 | Partial common structure | Medium; moderate match, unresolved regions |
| Main interpreter 2.02→3.02 V3 | Indeterminate | Low; insufficient coverage |
| Main interpreter 3.02 V3→3.6 | Partial common structure | Medium; substantial pairing, weak same-offset alignment and large unresolved areas |
| Main interpreter 3.6→3.6TT | Strong structural continuity | High for code structure; behavior untested |
| Run-only 1.0→2.02 | Partial common structure | Medium |
| Run-only 2.02→disk 3.02 `GFABASRO` (version 2.0) | Strong structural continuity | High for code structure; not evidence of a 3.02 runtime |
| Run-only 3.02 2.0→3.6TT 3.5 | Indeterminate | Low; minimal pairing |
| `GFACOM17`→3.6 compiler | Indeterminate | Inspect reports zero covered bytes; forced-68k listing yields very sparse pairs |
| Compiler E→D | Strong structural continuity | High for code structure; behavior/output untested |

## Proposed reconstruction lots

The following are candidate research lots, not implementations. They are ranked by evidence quality and dependency order; each should start with independently verified artifacts and a falsification probe.

1. **3.6 ↔ 3.6TT startup/environment matched spans.** Strong match at TEXT offset `$0000`; low dependency; verify GEMDOS call/data flow before routine naming.
2. **Compiler E/D shared core and altered operand sites.** P1 has high match coverage; low dependency; decode the 1,599 reference sites and remaining regions before semantic labels.
3. **Exact shared 3.6/TT utility programs and library format.** Exact hashes for three tools; medium dependency; identify GFA3BLIB record format before inferring link/runtime contracts.
4. **3.6/TT interpreter matched routine spans.** 22 high-confidence spans; medium dependency on call graph/string cross-references; map calls and data references first.
5. **Run-only 2.02 ↔ disk 3.02 runtime lineage.** High structural continuity but actual 3.02 role absent; verify exact internal version and compatible program fixtures.
6. **1.0 ↔ 2.02 interpreter and runtime initialization.** Moderate continuity; determine branch-resolved and unresolved entry behavior before subsystem slicing.
7. **3.02 V3 ↔ 3.6 transition.** Larger, riskier lot; use entry/call graph and strings to disambiguate, then probe selected spans in an emulator.
8. **3.02 V3 runtime identification and parser/variable candidates.** Low current match evidence; first identify a corresponding runtime/build artifact, then compare tokens and controlled programs.
9. **GFACOM17 compiler identification.** Highest uncertainty; establish file format and CPU/code regions independently before lineage analysis.

These lots can be handed off independently after common hash, offset, and evidence-tag conventions are agreed. No source reconstruction or behavior-equivalence claim is part of P2.
