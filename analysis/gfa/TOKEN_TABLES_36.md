# GFA 3.6 / 3.6TT table construction and token text lookup

## Question and evidence scope

This study asks what the tables built at TEXT `$1569E` contain, how the two
interpreters consume them, and whether they participate in parsing BASIC input
or in the separate dispatcher at `$1BD6`.

**OBSERVED:** the E executable is `work/extracted/p2/gfa-3.6/GFABASIC.PRG`
(SHA-256 `d44ca139e6712fd26c14abdf1d4480120a137b70919e1b9ac1c7813a532b4c39`)
and the D executable is
`work/extracted/p2/gfa-3.6tt/GFABASIC.PRG` (SHA-256
`b7706b9f9789c7ac3a9e06ded26aab55521e0c2552d2c51348ee0b87779adf6e`). Their
TEXT sizes are 102,288 and 102,460 bytes. Each full `rg-dis` listing recognizes
8,582 instructions and 25,932 code bytes; this is about 25.35% and 25.33% of
TEXT respectively, not whole-program coverage.

The focused listings were regenerated with `rg-dis` 0.11.46 and saved under
`work/rg/p3b-token-tables/`. The P3-A independent decoder was GNU
`m68k-atari-mint-objdump` 2.30. Hashes, commands, exact ranges and trace
provenance are in [TOKEN_TABLES_36_DATA.json](TOKEN_TABLES_36_DATA.json). The
Python model is [gfa_token_tables.py](../../tools/gfa_token_tables.py), and
the readable C reconstruction is in
[`token_tables.c`](../../reconstruction/gfa-3.6/token-dispatch/token_tables.c)
and [`token_tables.h`](../../reconstruction/gfa-3.6/token-dispatch/token_tables.h).

The disassembly ranges below are TEXT-relative. Static code and map ranges were
checked in both E and D listings. `named.veto` labels are not treated as proof
of executable code: the selected code sites have direct startup, branch, or
data-reference evidence. The two map bounds are established by the constructor
walking records up to a high-bit sentinel, not by an inferred function size.

## Findings

### Table builder and representation

**OBSERVED:** startup calls the constructor at `$1569E` and returns at `$1918`.
Its terminal `RTS` is `$1574E`. It first clears `$3D0` words beginning at
workspace `$D2C` (DBRA count `$3CF`), then fills two contiguous arrays:

| Array | Workspace offset | Capacity | Index form |
|---|---:|---:|---|
| Character spelling map | `$D2C` | 464 words | character key |
| Token spelling map | `$10CC` | 512 words | even byte offset into word table |

The arrays occupy 976 words / 1,952 bytes together. `$10CC = $D2C + 464*2`.
The first map ends at `$10CA`; this is the preceding word read when the second
map fills its first empty slot. The first character-map fill reads `$D2A`, which
the earlier startup clear sets to zero.

**OBSERVED:** the token source records begin at TEXT `$1111E` and end at the
sentinel at `$11EDA` (3,517 bytes including sentinel). Each record advances
`6 + prefix`; a high-bit prefix ends the map. Its key is a big-endian 16-bit
byte offset at `prefix+2`. That offset must be even because the store is a
word-indexed 68000 write. The source has 322 records, 299 unique keys and 23
duplicate-key records.

The character records begin at TEXT `$11EDB` and end at `$12CB8` (3,550 bytes
including sentinel). Each advances `4 + prefix`. The key byte at `prefix+3` is
used directly unless the discriminator at `prefix+2` is nonzero, in which case
`$E0` is added. There are 404 records, 397 unique keys and 7 duplicate-key
records. The first later record for a repeated key overwrites the previous
word; the final source record wins.

Both arrays store the low 16 bits of `record_TEXT_offset - $12CBA`. The values
are signed displacements when consumed by `ADDA.W`; the base is the static
record area at TEXT `$12CBA`. A single byte at `$12CB9` separates the final
character-map sentinel from that string base. The tool reconstructs the maps
without exporting the historical record bytes.

After insertion, the constructor forward-fills zero words from the previous
word. The character array's preceding value is the cleared workspace word at
`$D2A`; the token array starts with the last character-table word. It then
explicitly clears token-table word slots `$3C`, `$3F` and `$4C..$57`.

**OBSERVED:** the maps, their constructor code (`$1569E..$1574E`), and all four
selected read windows have byte-identical E/D contents. Both static rebuilds
produce SHA-256
`e273593ff6b9e36429c387019b238abcf270408e5070e25671c7e9f88e32e702` over the
1,952 big-endian table bytes. Full executable files and total TEXT lengths still
differ.

### Consumers and relation to parsing

**OBSERVED:** the renderer candidate at `$15276` reads the token map at
`$15296`. It loads a 16-bit token word, shifts it right once, and uses that
result as a byte displacement from `$10CC`; because the element is a word, the
map key corresponds to an even byte displacement. A nonzero result is
sign-extended by `ADDA.W` and added to the TEXT `$12CBA` string base. The
resulting record supplies bytes copied into the renderer output buffer.

The character map is read at `$1541C` after the decoded character byte is
doubled. The extended path at `$158E4` reads an additional byte, adds `$E0`,
doubles it, and uses the same map. Both paths resolve their word relative to
TEXT `$12CBA` and copy the associated record bytes.

**INFERRED, medium confidence:** these generated maps support spelling or
formatting token and character values for text/listing output. The exact
historical user-visible modes are not established by this bounded study.

The parser candidate at `$12EF6` directly loads static TEXT `$1111E` into A2
and compares its records with input bytes. That is a different access path from
the generated workspace map at `$10CC`. This weakens the idea that the two
workspace arrays are the primary BASIC input decoder. It does not establish
what every parser path does, and no complete parser semantics are claimed.

**OBSERVED:** the dispatcher at `$1BD6` is a separate mechanism. It reads an
advance word and D6 from an A5 frame, selects an indexed PC-relative longword
target into A0, and executes `JSR (A0)` at `$1BEC`. The static target vector has
26 longwords beginning at `$1BF8`. No static dataflow from either generated
map into the dispatch index was established. The dispatcher’s first vector
entry is TEXT `$869A`; the handler body was not followed.

### Bounded graph of table flows

```text
startup ($1912 JSR) -> builder ($1569E)
                         | reads static character map ($11EDB..$12CB8)
                         | reads static token map     ($1111E..$11EDA)
                         v
             workspace character map ($D2C, 464 words)
                         |                    \
                         |                     -> token map ($10CC, 512 words)
                         |                         ^
                         |                         | read at $15296
                         |                         +-- renderer candidate ($15276)
                         | read at $1541C and $158E4
                         +-- character text paths

parser candidate ($12EF6) -> static $1111E directly
dispatcher ($1BD6 / JSR $1BEC) -> separate 26-entry target vector
```

The graph stops at the first handler layer. It does not attribute functional
names to the 26 target routines.

## Dynamic checks under Atari TOS

Hatari 2.6.1 ran both executable copies under the same TT machine profile and
the same supplied Atari TOS 3.06 TT image (SHA-256
`974211d0f3db3d81af2d5c564df2e329fec48bb359a8b1eae9edacc9bbda7816`). Each
run used an isolated GEMDOS drive copy, the same debugger scripts and a
700-VBL limit. Raw memory captures and Hatari debugger logs are retained in
ignored `work/p3b/`; the JSON lists their exact paths and hashes.

**OBSERVED:** at TEXT `$1918`, immediately after the constructor returns, both
versions expose a 1,952-byte workspace snapshot equal byte-for-byte to the
static rebuild. E and D use different absolute workspace addresses (A6 is
`$27CF8` and `$27DA4`, a `$AC` difference), but the same `$D2C` and `$10CC`
offsets. The difference is reproducible in the same emulator and ROM; its
reason is not needed to establish the shared table layout.

For a controlled renderer input, a debugger script starts at `$15276` with a
synthetic 16-bit token word and a CR-terminated input. With word `$01CC`, the
renderer shifts to `$E6`, reads map word `$E478`, and resolves it to static
record TEXT `$11132` (`$E904 + $11132 = $1FA36` in the captured run). The
record is the last source record for key `$E6`. Both E and D have identical
table snapshots before and after the lookup and produce identical captured
output bytes (`27 20 41 0D 0A`).

A second controlled input uses word `$0160`. It selects token-map key `$B0`,
whose record at TEXT `$1185B` spells `PLOT`. The decoded character byte `A`
reaches the character lookup: at `$1541C`, the effective table byte offset is
`$82`; after the word load at `$15420`, D1 is `$F310`, resolving to character
record TEXT `$11FCA` (`ASIN(` followed by its stored marker and key). This
value and all 1,952 table bytes agree in E and D. These injections demonstrate
the machine operations and table-to-record relation; they are not a natural
BASIC source execution.

For the separate dispatcher check, a synthetic A5 frame sets D6 to zero and
control is directed to `$1BD6`. At `$1BEC`, Hatari reports A0 `$16F9E`, which
is runtime TEXT base `$E904` plus TEXT `$869A`, the first vector target. The
test resolves the indirect call but stops before executing the handler. It
does not demonstrate a natural parser-to-dispatch path.

An early malformed renderer fixture omitted the required CR. It read beyond
the six-byte synthetic input and the workspace table snapshot changed before
the dispatcher breakpoint. That run is retained as a falsification result,
not treated as normal behavior. Adding the CR made the input bounded and kept
the map stable through both table lookups. The direct renderer invocation can
still enter cleanup paths absent a real caller context, so only the captured
lookup instructions and their pre-handler data are asserted here.

The supplied TOS 1.04 Mega ST, 1.06 STE, 1.62 STE and 3.06 TT images were also
probed with Hatari `--run-vbls 2` using `megast`, `ste`, `ste` and `tt`
profiles respectively; all exited 0. The 1.62 archive member is 262,145 bytes
and was tested untrimmed. No local EmuTOS image was found in the searched
system/project ROM locations, and none was downloaded. No claim here is an
EmuTOS observation.

## Validation, confidence and open questions

The Python reconstruction and tests cover record termination, record bounds,
big-endian keys, array capacities, forward-fill order, the contiguous-table
predecessor, explicit zero slots, invalid odd/out-of-range indices, duplicate
last-write behavior, and a semantic-key change that changes generated bytes.
The altered-key fixture is a falsification check: the changed output must not
be reported identical. Dynamic E/D snapshots independently validate the
resulting historical table bytes.

| Claim | Status | Confidence |
|---|---|---|
| Two array sizes, bases, record rules and fill behavior | OBSERVED statically; matched dynamically | High |
| E/D source maps, constructor, selected consumers, rebuilt tables | OBSERVED exact equality | High for bounded ranges |
| Workspace tables are used for spelling/formatting | INFERRED from loads and copied output records | Medium |
| Workspace tables drive parser tokenization | Not established; parser candidate reads static `$1111E` directly | Low / open |
| Generated maps select `$1BEC` handlers | No dataflow found | UNMEASURED |
| Natural BASIC execution reaches these specific reads and dispatcher entry | Not exercised | UNMEASURED |
| Behavior under original Atari ROM on hardware | Hatari Atari TOS image used; no physical hardware | UNMEASURED |

### Reproduction commands

```sh
rg-dis work/extracted/p2/gfa-3.6/GFABASIC.PRG --arch 68k --cpu auto --machine st --quiet --no-annotate-gfa --no-smart-labels --annotate-offsets -o work/rg/p3b-token-tables/36E.s
rg-dis work/extracted/p2/gfa-3.6tt/GFABASIC.PRG --arch 68k --cpu auto --machine tt --quiet --no-annotate-gfa --no-smart-labels --annotate-offsets -o work/rg/p3b-token-tables/36D.s
python3 tools/gfa_token_tables.py work/extracted/p2/gfa-3.6/GFABASIC.PRG --json
python3 tools/gfa_token_tables.py work/extracted/p2/gfa-3.6tt/GFABASIC.PRG --json
cc -std=c99 -Wall -Wextra -Werror -c reconstruction/gfa-3.6/token-dispatch/token_tables.c -o work/p3b/build/token_tables.o
make test
```

The Hatari scenarios use the launch and breakpoint scripts retained beneath
`work/p3b/fixtures-d/`, `fixtures-e/`, `fixtures-d-char/` and
`fixtures-e-char/`. Raw logs and snapshots are under `work/p3b/traces/`.
Exact run options, ROM inventory and each evidence SHA-256 are in the JSON
companion.

### Next questions

P3-C should provide a valid GFA tokenized input or a normal interactive session
and capture the parser’s input representation, then trace a natural path into
the A5 dispatcher frame. This would test whether parser-produced token values
are related to the text maps or only to the separate handler vector. Keep the
first experiment bounded to one known token and one character; do not expand
into all parser branches or handler bodies.
