# GFA BASIC 3.6 startup path (E / TT D)

## Question, artifacts, and scope

This note follows the GEMDOS entry path of the two interpreter PRGs up to the first token-handler dispatcher. It reconstructs initialization stages whose data flow is visible; it does not claim that the entry preamble is a complete function or reconstruct the whole interpreter.

| Artifact | Distribution member | Executable SHA-256 | PRG sections TEXT / DATA / BSS |
|---|---|---|---|
| E | GFA 3.6 `GFABASIC.PRG` | `d44ca139e6712fd26c14abdf1d4480120a137b70919e1b9ac1c7813a532b4c39` | 102,288 / 36 / 1,088 |
| D | GFA 3.6TT `GFABASIC.PRG` | `b7706b9f9789c7ac3a9e06ded26aab55521e0c2552d2c51348ee0b87779adf6e` | 102,460 / 36 / 1,088 |

Both binaries identify as 3.60 TT interpreters; E additionally carries the `3.6 TT E` marker. Hashes are of extracted PRGs, not disk images. The full inventory is in [INVENTORY.md](INVENTORY.md). Listing offsets in this report are TEXT-relative. For conventional GEMDOS loading, the image is based at `$10000`; file offsets are TEXT offsets plus the 28-byte PRG header. Data/BSS labels shown by the listing are relocated addresses.

## Method and reproducibility

**OBSERVED:** fresh `rg-dis` listings were produced with pinned `rg-dis` 0.11.46 (SHA-256 `1a66448a2a3215ded9e89515f3e0c5fbb02e7d05ec9e8bc175dda492734bc4ef`). An independent 68000 disassembly of extracted TEXT slices was produced with GNU `m68k-atari-mint-objdump` 2.30 (SHA-256 `e4fe8b8f4088837bc24ee27058b358e5375090737399f6a12c4f822f56a87bca`). Receipts, slices, raw listings, and region/relocation/function JSON are retained under ignored `work/rg/p3a-startup/`; neither source binaries nor earlier listings were changed.

```sh
rg-dis work/extracted/p2/gfa-3.6/GFABASIC.PRG --arch 68k --cpu auto --machine st --quiet --no-annotate-gfa --no-smart-labels --annotate-offsets -o work/rg/p3a-startup/36E.s
rg-dis work/extracted/p2/gfa-3.6tt/GFABASIC.PRG --arch 68k --cpu auto --machine tt --quiet --no-annotate-gfa --no-smart-labels --annotate-offsets -o work/rg/p3a-startup/36D.s
rg-dis work/extracted/p2/gfa-3.6/GFABASIC.PRG --arch 68k --machine st --quiet --json --inspect regions --record-decisions -o work/rg/p3a-startup/36E.regions.json
rg-dis work/extracted/p2/gfa-3.6tt/GFABASIC.PRG --arch 68k --machine tt --quiet --json --inspect regions --record-decisions -o work/rg/p3a-startup/36D.regions.json
```

The independent decoder confirms the actual entry edges through ranges that `rg-dis` calls `named.veto`. That label is not treated as evidence of code by itself. For this scope, executed instruction flow and independent decoding establish code at `$0026..$0043` and `$181C..$1BD3`; `$1A96..$1A9F` remains a data/unknown gap and is not promoted to code. The broader P2 matched span `$0000..$0306` (322 instruction pairs) is a structural candidate only, not a startup-function boundary.

## Startup path and boundary

```text
GEMDOS entry TEXT:$0000
  -> tiny entry branch and environment stub ($0000..$0043)
  -> initialization body ($181C..$1974)
  -> interactive fallback ($1978..$1AC4) or command-line path
  -> shared initialization/console helper ($1B16..$1BD3)
  -> token dispatcher boundary ($1BD6; indirect handler call at $1BEC)
```

**OBSERVED:** `$0000` branches to `$0026`. The initial bytes `$0002..$0025` are data, including an ESC sequence. At `$0026`, code copies the first word of that sequence into the BSS output buffer at `$1B5E`, fills four longs at the BSS sentinel with `$FFFFFFFF`, and jumps to `$181C`. The reachable path therefore skips the intervening TEXT range; the `$0000` preamble and the initialization body are separate blocks.

At `$181C`, the program obtains the basepage from `4(A7)` into A5 and locates its BSS workspace in A6. It rounds A6 up to a 4-byte boundary, clears `$9000` bytes using `$900` iterations of a 16-byte zeroing loop, and writes the global workspace pointer. It places a 26-entry absolute-jump stub table at A6+$D6 from the 26 longword targets at TEXT `$17B4..$181B`. The table is byte-identical in E and D. It then sets workspace state, installs a return trampoline, and records basepage and memory-size values in the workspace.

Next, at `$1878..$1896`, it calls GEMDOS `Mshrink` (TRAP #1, function 74) with the basepage and size computed from the chosen workspace end. This matches the TOS parameter order described in Atari's [GEMDOS programming manual](https://www.bitsavers.org/pdf/atari/ST/Atari_ST_GEM_Programming_1986/GEM_0042.pdf). The return value is not tested in this path. The call is followed by opaque internal calls at `$1898` and `$189E`.

The visible machine-service setup then queries the screen base with XBIOS `Logbase` (#3, `$18B8`), queries resolution with `Getrez` (#4, `$18C2`), and executes Line-A initialization (opcode 0, `$18CC`). It stores the returned Line-A variables, font table, and screen base pointers. Calls to XBIOS functions and Line-A are decoded from the immediate function numbers and trap/opcode sequence; the external ABI descriptions are in the [Atari Compendium](https://ftp.pigwa.net/stuff/collections/Atari%20documents/Manuals/The_Atari_Compendium.pdf) and [Line-A reference](https://www.atari-wiki.com/index.php?title=Line_A).

At `$18DE..$18F8`, the code calls GEMDOS `Malloc(-1)` to query the largest block, subtracts `$4000`, then requests that amount with a second `Malloc`. It stores the returned size and pointer in A6-relative globals, without an apparent null check. This is a visible flow, not proof of what later code does on allocation failure. Atari's Compendium documents the `Malloc(-1)` convention. A second-stage allocation is plausible as a reserve/work-area setup; the exact intended use remains **INFERRED**, not named from position alone.

The path then calls helper candidates at `$1902`, `$190A`, `$190E`, `$1914`, `$1918`, `$191C`, and `$1920`. The strongest data-flow candidate is `$190A` → `$1569E`: it clears two tables and fills them from static maps, consistent with token/character lookup initialization. This routine is not part of the narrow startup reconstruction and should be checked as a separate parser-table task.

At `$1924..$1974`, command-tail handling uses basepage field `$80`. TOS defines this as a length-prefixed command tail. The code reads the leading length byte, tests for zero, skips spaces, accepts an optional `-`, skips more spaces, then copies bytes into workspace buffer A6+$452 until a NUL byte. The visible loop has no bound check. **HYPOTHESIS / UNMEASURED:** the code may depend on a terminating NUL or adjacent memory contents; the GEMDOS manual notes that command-tail termination is not guaranteed. No overrun is claimed without a controlled run. The zero-length and subsequent failure paths enter the prompt/fallback path at `$1978`.

The fallback resets stack and flags, invokes opaque display/environment helpers, and enters the prompt loop at `$19CC`. It prints one of two ESC-prefixed prompts via the output routine at `$F914`. The loop calls parser candidate `$12DF6`, whose implementation is outside scope. Error paths reference localized strings (E: “Syntax Error”, “Line too long”; D: “Syntax Fehler”, “Zeile zu lang”). The successful command-line route and prompt route converge on `$1B16`, then reach `$1BD6`.

At `$1BD6`, A6 is reset from a global workspace pointer and command/token state is read before a table-selected handler is invoked indirectly with `JSR (A0)` at `$1BEC`. This is the boundary of this reconstruction. Handler resolution and post-dispatch behavior are not reconstructed.

## Local dependency graph

Addresses below are TEXT offsets in both images unless indicated. “Caller” lists only observed edges in or directly relevant to the startup slice; this is not a whole-program call graph.

| Candidate routine / range | Observed callers → callees | Registers, parameters, data, effects | Services / confidence |
|---|---|---|---|
| Entry stub `$0000..$0043` | GEMDOS entry → `$181C` | Reads ESC word at `$0002`; writes BSS output prefix `$1B5E` and four BSS sentinel longs; jumps directly | No trap; high for edges and effects, medium as a named “environment stub” |
| Main init `$181C..$1974` | `$003E` → `$1898`, `$189E`, `$18B8`, `$18C2`, `$18CC`, `$18D6`, `$18DE`, `$18F2`, `$1902..$1920`, then branches to `$1978` or command processing | A5=basepage; A6=aligned workspace; A7 reset to workspace+$6500; writes globals and tables; installs vector stubs and trampoline | GEMDOS Mshrink/Malloc, XBIOS Logbase/Getrez, Line-A init; high for sequence and direct services, medium for workspace purpose |
| Vector stub builder `$184C..$186E` | main init → table at `$17B4` | A0 points to workspace+$D6; copies 26 longword targets into 26 six-byte `JMP abs.l` stubs; uses D0/D1/A0 | No external service; high |
| Table rebasing `$A94C..$A9??` | init `$1898` → `$A94C` | D0=21, D1=A6; adds A6 to 22 longword entries at `$A960..$A9B7` | Internal; high for count and transformation, function purpose unmeasured |
| Palette capture `$A610..$A62?` | init `$189E` → `$A610` | Iterates 16 palette indices; XBIOS #7 Setcolor result stored through table `$LA72A` | XBIOS Setcolor; high for service/loop, medium for “capture” intent |
| Display reinit candidate `$A632..$A693` | prompt/fallback helpers → `$A632` | Reads saved resolution `$206C`; uses screen base `$C0`, palette and Line-A state | XBIOS Getrez/Setcolor and Line-A; medium |
| Command setup `$1902..$1923` | main init → `$A422`, `$A424`, `$1569E`, `$1B16`, `$A72A` | Sets globals and builds lookup tables; exact parameter contracts mostly opaque | Internal; medium for lookup-table builder, low for surrounding names |
| Command-tail reader `$1924..$1974` | main init → command path or `$1978` | A5 basepage; A0 from basepage+$80; writes A6+$452; scans for NUL without visible bound | No direct service; high for operations, low for intended bound/termination contract |
| Prompt/fallback `$1978..$1AC4` | init branch → `$4EF8`, `$A632`, `$ED??`, `$4F12`, `$A694`, `$A0B0`, `$12DF6`, `$1BD6` | Resets stack/flags; emits prompt; invokes parser; error strings differ by language | Some helper calls include GEMDOS/XBIOS elsewhere; medium for prompt-loop identification, low for opaque calls |
| Startup reset `$1B16..$1B75` | prompt/fallback → `$1BA0`, `$A694`, `$CF84`, `$F914`, `$BA0A`, `$A4AA`, `$A0B0`, `$79FC`, `$ACA2` | Clears several globals; prints ESC sequence; D0=0 and later D0=78 passed to AES parameter helper | AES TRAP #2 downstream; medium for reset/output role; AES function meaning unresolved |
| Mouse/Line-A guard `$1B7C..$1BCF` | output helpers via `$ECE2/$ECE8` → `$1BA0/$1B7C` | Checks Line-A state; saves/restores D0-D2/A0-A2 around Line-A calls; temporary pointer at Line-A vars+8 | Line-A opcodes #9/#10 (show/hide mouse); high for opcodes/register preservation, medium for guard purpose |
| String output `$F914..$F92?`; char output `$FC88..$FC??` | prompt/reset → `$F914` → `$FC88` | A0=NUL-terminated string; saves D0-D2/A1-A3; byte loop emits chars | BIOS TRAP #13 Bconout (#3, device #2); high |
| Token dispatcher boundary `$1BD6..` | startup → `$1BD6`, indirect `JSR (A0)` at `$1BEC` | Reinitializes A6 and selects handler through table; indirect target set is not resolved here | No reliable handler inventory in this scope; boundary only |

Routine end addresses with `??` are intentionally uncertain where a tight semantic boundary has not been established; see the exact listing under `work/rg/p3a-startup/`. The graph is local and omits calls whose targets are outside the selected initialization flow.

## D/E equivalence table

Comparison scope: entry `$0000..$0043`, init/prompt path `$181C..$1BD3`, plus the two referenced tables below. The main instruction denominator is 252 decoded instruction rows (9 + 243); 248 rows are instruction-and-operand identical at corresponding offsets, and 4 rows differ only in `LEA` address operands. This is a scoped listing count, not whole-TEXT coverage. Raw bytes differ at 2/68 bytes in the entry span and 6/952 bytes in `$181C..$1BD3` (8/1,020 total). Direct control-transfer targets and branch structure are the same.

| Reconstructed function / data | E address | D address | Classification | Confidence / evidence |
|---|---:|---:|---|---|
| Entry stub | `$0000..$0043` | `$0000..$0043` | Structural identity; one BSS `LEA` target relocated | High; same edges/effects, 8/9 instruction rows exact |
| Main init and command tail | `$181C..$1974` | `$181C..$1974` | Structural identity; workspace BSS `LEA` target relocated | High for control flow, medium for opaque helper semantics |
| Prompt / fallback | `$1978..$1AC4` | `$1978..$1AC4` | Same control structure, language-specific strings and some data addresses | Medium; parse/error path opaque |
| Reset and mouse helpers | `$1B16..$1BCF` | `$1B16..$1BCF` | Instruction-identical at corresponding offsets | High for mechanically observed behavior |
| String/character output | `$F914` / `$FC88` | `$F914` / `$FC88` | Instruction-identical at corresponding offsets | High for BIOS output primitive |
| Error string references | `$1A5A → $17458`; `$1A70 → $17468` | `$1A5A → $17504`; `$1A70 → $17515` | Real localized data difference (English vs French), address also moved | High; bytes/string content and relocation entries verified |
| Jump-stub target table | `$17B4..$181B` | `$17B4..$181B` | Exact data identity, 26/26 longwords | High; raw bytes compare equal |
| VDI/AES offset table | `$A960..$A9B7` | `$A960..$A9B7` | Exact data identity, 22/22 longwords | High; raw bytes compare equal |

Across entry plus initialization through `$1BD3`, there are 40 conditional/unconditional branch instructions, 44 direct calls, and 2 JMP instructions, for 86 direct statically resolved transfers. All 86 targets/operands agree between E and D; one additional transfer is an indirect JMP and remains unresolved. These are counts from the scoped listing, with `JSR`/`BSR` counted separately from branch mnemonics. The subsequent dispatcher contains another indirect `JSR`, outside these counts. Four absolute `LEA` extension-word relocation sites at file-loaded code offsets `$10032`, `$11822`, `$11A5C`, `$11A72` are present in both relocation maps; they account for the BSS/string address changes. No other code differences were observed in these spans.

**Conclusion:** a shared historical startup implementation with relocated workspace/string addresses and localized error text is supported. The result establishes structural continuity, not behavioral equivalence. Full-image P2 comparison independently reports 4,327 candidate pairs / 4,329 E rows and 4,355 D rows, 4,324 exact pairs, 3 changed reference operands, and 920/920 verifiable candidate branches equal; its filtering excludes `named.veto` and unknown regions.

## Hypotheses, falsification, and limits

| Claim | Tag | Falsification check / status |
|---|---|---|
| `$181C` is the initialization body reached from the entry stub | OBSERVED | Independent objdump verifies `$0000 → $0026 → $181C`; falsified if decoding shows another edge or bytes differ from extracted TEXT. Reproduced. |
| `$184C` installs callable six-byte jump stubs from the table at `$17B4` | INFERRED | Compare each emitted opcode/target with each table word; 26/26 table words match E/D, loop count is 26. Dynamic indirect-call trace remains UNMEASURED. |
| `$18DE` asks for the largest free block and then reserves it minus `$4000` | OBSERVED / INFERRED | Trap immediate and D0 arithmetic are visible. Falsify by tracing D0 at both traps; no emulator run. Whether subtraction avoids later exhaustion is UNMEASURED. |
| Command-tail copy is safe for all GEMDOS command tails | HYPOTHESIS rejected as established fact | Static loop has no visible bound and scans for NUL. The manual describes a length-prefixed tail and does not guarantee the terminator; a controlled Hatari run with boundary-length tails is needed to determine actual outcome. No safety conclusion is made. |
| E and D startup paths share the same control implementation | OBSERVED structurally | Compare all direct targets and operands over the stated ranges and inspect relocation records: 86/86 direct targets agree; changed operands are the four LEAs listed above. |
| Helpers `$A632`, `$A424`, `$8D6C`, `$E264` have fully identified semantics | UNMEASURED | Follow their full data/call graphs and test effects under a controlled TOS; no semantic labels assigned here. |

`Hatari v2.6.1` is installed and supports ST/TT plus an explicit `--tos` ROM option. No usable TOS ROM was found in `/usr/share/hatari` or `work/`. No ROM was downloaded. Dynamic execution is therefore **UNMEASURED**. With a legally available ROM, a reproducible next experiment is to run each exact PRG under a fixed TT machine/profile, capture GEMDOS/XBIOS/Line-A traps and memory writes through the first indirect handler call, and repeat with zero-length, maximum-length, and deliberately boundary-positioned command tails. Save ROM hash, Hatari version/options, disk/PRG hash, and trace.

## Unresolved regions and next handoff

The preamble does not establish a semantic boundary around the 322-instruction P2 candidate. The main init body contains opaque helper calls. The command parser at `$12DF6`, dispatcher targets, and most of the large interpreter remain outside scope. `$1A96..$1A9F` is not decoded as code. Static-analysis coverage in the two full interpreters is only 25,932 covered bytes out of 102,288 E TEXT and 102,460 D TEXT (rg-dis summary); this startup study validates a selected path, not the rest of TEXT. Region decisions, relocations, and all generated evidence are retained under `work/rg/p3a-startup/`.

The best next bounded subsystem is lookup-table construction around `$1569E`, reached during startup and supplied by static maps at `$1111E` and `$11EDB`. Its table sizes and consumers can be followed independently, then connected to parser `$12DF6`. An alternative is the line editor / command-tail input path; first establish a controlled command-tail contract and then trace `$8D6C`/`$E264`. See [P3A_HANDOFF.md](P3A_HANDOFF.md).
