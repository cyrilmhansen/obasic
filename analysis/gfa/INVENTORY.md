# GFA BASIC binary inventory

## Scope and provenance

This inventory covers the five ST images already present in `work/disks/` and their files as enumerated by the corresponding `work/inventory/*.json` reports. No network retrieval was needed. Full hashes, member paths, sizes, extraction notes, and duplicate groups are in [LINEAGE_DATA.json](LINEAGE_DATA.json).

| Distribution label | Image | Bytes | SHA-256 |
|---|---|---:|---|
| GFA BASIC 1.0 | `work/disks/gfa_basic_gfa_systemtechnik.st` | 737,280 | `da945b602a24ed75a8357264ae4c221cadc293533f158c089d5d7a6ee1b3ca1f` |
| GFA BASIC 2.02 | `work/disks/GFA Basic v2.02 (1987-09-15)(GFA Systemtechnik).st` | 737,280 | `81b32574ecb9915922969ba84bb6ccfe16aba9eaf994ffe99dda11ea5920ac4e` |
| GFA BASIC 3.02-labelled disk | `work/disks/GFA Basic v3.02 (19xx)(GFA Systemtechnik).st` | 839,680 | `4bd9714a77bb5d01a9016cd9a0674560b1ca59d242f529064efae5c1ea63d636` |
| GFA BASIC 3.6 | `work/disks/GFA Basic v3.6 (1991-05-06)(GFA Systemtechnik).st` | 737,280 | `ed98931c7b57b501c3dbe3f14704d0bdf1ef75e2bca8f35554d34455e4dda842` |
| GFA BASIC 3.6TT | `work/disks/gfa_basic_3_6tt_gfa_systemtechnik.ST` | 819,200 | `5f1652b68833b1f75666f4f6a5920bb0389db3a8ae986dcaed8100bb9a0b5615` |


`rg-dis` is version 0.11.46, executable SHA-256 `1a66448a2a3215ded9e89515f3e0c5fbb02e7d05ec9e8bc175dda492734bc4ef`. The disassembly summaries below were generated from extracted executables with `rg-dis --inspect cpu` and `--inspect summary`. “Instruction bytes” means `covered_bytes` as reported by rg-dis, not all text bytes.

## Principal interpreters, runtimes and compilers

Every executable hash below is for the extracted PRG itself, not the disk image.

| Distribution/member | Identified role and version evidence | Bytes; TEXT/DATA/BSS | Relocations | rg-dis instructions / covered bytes; minimum CPU | Executable SHA-256 |
|---|---|---:|---:|---|---|
| 1.0 `GFABASIC.PRG` | Interpreter by filename and distribution; internal release string not verified | 54,038; 52,742/0/0 | 1,198 | 3,991 / 12,590; 68000 | `f64f180134ab211567b5373f1e3150e06d0dde27b00be671f1a4429b73382d6f` |
| 1.0 `GFABASRO.PRG` | Run-only role and “RUN-ONLY Version 1.0” string, offset `$5696` | 40,301; 39,314/0/0 | 907 | 1,257 / 4,098; 68000 | `774c94b0425feac0f377008599cda60295f5a248f28164523b54a28855f9d43b` |
| 2.02 `GFABASIC.PRG` | Interpreter, internal “Version 2.02”, offset `$D366` | 57,613; 56,276/0/0 | 1,229 | 4,413 / 13,746; 68000 | `368977ec55f4a1f03ab54ed695756757dfcb75d7a9ae2158640315d66256888f` |
| 2.02 `GFABASRO.PRG` | Run-only runtime, internal “Version 2.02”, offset `$95AA` | 41,451; 40,472/0/0 | 898 | 1,537 / 4,862; 68000 | `3b9fad39d0f4cd74547117838b217bea2819c4d5b378a30e347ef1e64cf1460a` |
| 2.02 `GFA_ASM/GFABASIC.PRG` | Bundled older interpreter copy, internal “Version 2.0”, offset `$CEBA` | 56,409; 55,074/0/0 | 1,232 | 4,368 / 13,626; 68000 | `0460b4ec45a8837f9ed2f077bd85921b934cbbd0b00c675a45ea23d32a4b872a` |
| 2.02 `GFA_ASM/GFACOM17.PRG` | Compiler candidate from path/name; compiler revision is not internally verified | 53,472; 53,064/0/0 | 333 | 0 / 0; CPU not measured | `9fae43fcb2ad1f6190323bf20e75ea21a2cc5e7e16275365ae8fb01a65b7a409` |
| 3.02 disk `GFABASIC.PRG` | **Not identified as 3.02:** its internal string says “GFA BASIC V 2.0 US”, offset `$CE48` | 56,128 recovered; 54,794/0/0 | 1,232 | 4,366 / 13,618; 68000 | `a1f6989ff9742046a8e85c5c0df7a2f00679728192942ae17052cdb7d2db6536` |
| 3.02 disk `GFABASRO.PRG` | Run-only runtime identifies programs as GFA BASIC 2.0 (French diagnostic), offset `$8F49` | 41,596; 40,620/0/0 | 894 | 1,540 / 4,872; 68000 | `b6afd974355acf29764c0fc2012fa790b89b8be45f4117b5c472d7f06dc6a86d` |
| 3.02 disk `GFABASV3.PRG` | Main 3.02 interpreter candidate; menu says Version 3.02 at `$E1E9`, embedded marker “3.02 E” at `$15D66` | 92,674; 90,780/36/256 | 1,603 | 7,465 / 22,402; 68000 | `1f1b3e7f10e189863f1981df5ec023caeb912c457fa5db9f69a798166436c9a9` |
| 3.6 `GFABASIC.PRG` | Interpreter; internal menu says Version 3.60 TT at `$EB85`, another marker says 3.6 TT E | 104,597; 102,288/36/1,088 | 2,024 | 8,582 / 25,932; 68020 | `d44ca139e6712fd26c14abdf1d4480120a137b70919e1b9ac1c7813a532b4c39` |
| 3.6 `COMPILER/GFA_BCOM.PRG` | Compiler, internal “GFA-BASIC Compiler 3.6 TT E”, offset `$000E` | 73,070; 65,046/7,284/18,662 | 532 | 6,023 / 18,068; 68000 | `a2ffa32cdf46079821721dd22b9284c446d944492bd242f661f96ab5d69991bc` |
| 3.6TT `GFABASIC.PRG` | Interpreter; internal menu says Version 3.60 TT at `$EB85` | 104,770; 102,460/36/1,088 | 2,024 | 8,582 / 25,932; 68020 | `b7706b9f9789c7ac3a9e06ded26aab55521e0c2552d2c51348ee0b87779adf6e` |
| 3.6TT `GFABASRO.PRG` | Run-only runtime; internal banner says “GFA-BASIC 3.5 RUN ONLY”, offset `$CEDC` | 70,500; 68,604/4/640 | 1,728 | 2,131 / 6,428; 68000 | `993592ff472bac9bb8ac2a965464f8fb32c02ea6b20cf465101f0cd993525015` |
| 3.6TT `GFA_BCOM.PRG` | Compiler, internal “GFA-BASIC Compiler 3.6 TT D”, offset `$000E` | 73,091; 65,062/7,290/18,662 | 532 | 6,023 / 18,068; 68000 | `47b4527a00656d840ab4a76ccba2e718cbd6e7abe162b6da75167cd1344290e8` |

Identification confidence is high when the executable itself contains an explicit release/role marker. It is medium where the role follows only from packaging and filename. A filename, disk label, or `rg-dis` runtime annotation alone is not an internal version proof.

## Other executable and object members

The complete per-member list and SHA-256 catalog contains 47 active directory members selected from GEMDOS executable flags and executable/object extensions. It includes secondary printer, assembler, sprite, RCS, and editor tools, plus `.O` files. `.O` is not treated as a format: `C_TST.O` is a DRI relocatable object, while TT `TEST.O` and `TESTX.O` are TOS-format files. The two `ASSEM.BAK` copies are byte-identical to each other but `rg-dis` rejects their declared section sizes; they are not counted as valid executable lineage.

Important secondary executable members from the actual inventory:

- **2.02:** `PRINTER/PTEPSON.PRG`, `PTGRAPH.PRG`, `PTIBM.PRG`, `PTTYPE.PRG`; `GFA_ASM/ASSEM.PRG`; and the duplicated `GFA_ASM/GFABASIC.PRG` / `GFACOM17.PRG` copies at two folder depths.
- **3.02:** `PRINTER/SMM_804.PRG`, `PRINTER/EPSON.PRG`, `SPRITES/EDSPRT.PRG`, `BLITTER.PRG`, `VERTRAST.TOS`, `DCOPY19.TOS`.
- **3.6:** `COMPILER/GL.PRG`, `MAKE_NDX.PRG`, `MENU.PRG`, `RCS/DEF2DFN.PRG`, `RCS/RCS2.PRG`.
- **3.6TT:** `GL.PRG`, `IMMUN.PRG`, `MAKE_NDX.PRG`, `MENU.PRG`, `PTEPSON.PRG`, `PTIBM.PRG`, `DEF2DFN.PRG`, `RCS2.PRG`, `TEST.O`, `TESTX.O`.

The v2.02 image also contains a deleted directory entry `?FACOM17.PRG`; it is not an active file and was not extracted or counted as an executable.

## Exact duplicate findings

**OBSERVED:** the two copies each of `GFA_ASM/ASSEM.PRG`, `GFA_ASM/GFABASIC.PRG`, and `GFA_ASM/GFACOM17.PRG` in the 2.02 image are exact byte-identical duplicates. The two `ASSEM.BAK` entries are also identical to each other, but invalid as complete executables.

**OBSERVED:** these 3.6/3.6TT programs are exact cross-image executable duplicates:

| Member in 3.6 → member in 3.6TT | Bytes | SHA-256 |
|---|---:|---|
| `COMPILER/MAKE_NDX.PRG` → `MAKE_NDX.PRG` | 1,420 | `7a8a41839b9ea50f954e96ed82bd9b1e37fda3b5b9e5d2f4ccbeb1d0b68d61f7` |
| `RCS/DEF2DFN.PRG` → `DEF2DFN.PRG` | 13,971 | `54f843d3a51fcce00b8ad426ba6964552f958811b1126cf9b83b5209a8a3f001` |
| `RCS/RCS2.PRG` → `RCS2.PRG` | 96,083 | `218e58154564430357328fcb0db35e729640f562f4c4e645e2c8943c77bd2750` |

The `C_TST.O` members are also identical (116 bytes, SHA-256 `64b16fbc707d6566372cc5dcd00b744c45ee445fa40d019e7347be22b377a87c`) and both identify as DRI objects rather than standalone executables.

## Libraries and 3.02 recovery

`GFA3BLIB` is present under `COMPILER/` in 3.6 and at disk root in 3.6TT. The filename and placement support “compiler library candidate,” but its internal format and exact runtime role are not yet validated. The 3.6 file is 139,462 bytes (SHA-256 `06be1de2d9d4630ef82621bb28c9c0189f92d760121e5445fd99c2b2176f2e53`); 3.6TT is 139,766 bytes (`036b89f157c9cbaaa1a42837088c90999a96fd0599abeff208d73004916b5752`). A raw byte sequence comparison aligns 138,335 bytes, longest exact run 124,399, while only 55,492 bytes match at identical offsets. The `.NDX` files have equal 32,527-byte lengths, different hashes, and 31,907 bytes aligned by sequence. These are data-level observations, not identified routine matches.

**OBSERVED — malformed 3.02 directory size:** the FAT inventory says `GFABASIC.PRG` is 64,320 bytes, but its active chain contains only 55 clusters (56,320 bytes). `rg-dis` independently reads a complete GEMDOS PRG header with TEXT 54,794 and 1,232 relocations. `tools/extract_st_member.py --recover-gemdos` follows only available FAT bytes and trims at the validated relocation terminator, yielding a 56,128-byte PRG. There are 192 bytes after the relocation terminator in the reachable chain; the missing 8,000 bytes promised by the directory entry were not invented. Both the original-container inspect and recovered-PRG inspect report the same TEXT size and relocation count. All other extraction paths are strict.

## Reproduction and limits

The reproducible extractor, 3.02 recovery command, `rg-dis` receipts, CPU summaries, raw listings and per-range classifications are recorded in `LINEAGE_DATA.json` and ignored `work/` evidence. Core disassemblies use `rg-dis --arch 68k --no-annotate-gfa --no-smart-labels --annotate-offsets`; all CPU summaries use version 0.11.46. Structural candidate counts exclude `named.veto` ranges but can still differ from `rg-dis` CPU totals. An unpaired member or absent instruction match is not evidence of a rewrite.

**UNMEASURED:** executable behavior, compiler output compatibility, and any routine family not supported by explicit code/data cross-references or a controlled emulator run.
