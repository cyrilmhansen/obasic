# P3-C3 — Corps cible TEXT $5D04 et frontière de sortie (PRINT "A", PRINT 1+2)

## Question et binaire

Question : pour les deux lignes P3-C2 acceptées (`PRINT "A"`, `PRINT 1+2`), prouver l'entrée
naturelle dans la cible sélectionnée TEXT `$5D04` (runtime `$14608`, base TEXT `$E904`),
capturer la portion bornée du corps, et borner la frontière de sortie immédiate sous E et D.
Aucune injection de buffer ou de registre ; aucune généralisation au-delà de ces deux cas.

| Artefact | Valeur |
|---|---|
| GFA E `work/extracted/p2/gfa-3.6/GFABASIC.PRG` | SHA-256 `d44ca139e6712fd26c14abdf1d4480120a137b70919e1b9ac1c7813a532b4c39` |
| GFA D `work/extracted/p2/gfa-3.6tt/GFABASIC.PRG` | SHA-256 `b7706b9f9789c7ac3a9e06ded26aab55521e0c2552d2c51348ee0b87779adf6e` |
| ROM TOS 3.06 TT en-GB `work/p3b/roms/tos306-tt-gb.img` | SHA-256 `974211d0f3db3d81af2d5c564df2e329fec48bb359a8b1eae9edacc9bbda7816` |
| Hatari | 2.6.1, `/usr/bin/hatari`, SHA-256 `98d3879baf70b6e140071994ebebd791b148f72b9115c1dc512865123d0faa77` |
| rg-dis | 0.11.46, `/usr/local/bin/rg-dis`, SHA-256 `1a66448a2a3215ded9e89515f3e0c5fbb02e7d05ec9e8bc175dda492734bc4ef` |
| Profil clavier | `tools/hatari_gfa_scancode.cfg`, SHA-256 `758f98d8015eb8b1c37bfa86b458dcf421c784c97fb2aaffdb7deb69d9c79df0` |

Huit exécutions sous `work/p3c3/` : par variante (E/D) et ligne, un run `output`
(`:file` debugger jusqu'à la frontière, exécution naturelle continue) et un run `steps`
(tentative d'historique single-step). Conduits par `work/p3c3/run_target_case.py` ; la
correction de steps est `work/p3c3/run_steps2.py` (un seul cas tenté, échec documenté).

## OBSERVED — entrée naturelle bornée, identique E/D

Les quatre runs `output` atteignent le point d'appel indirect `JSR (A0)` TEXT `$1BEC` avec
A0=`$14608`, D6=`$024C`, puis le breakpoint d'entrée `$14608` avec le buffer parser
octet-exact (`PRINT "A"` = `50 52 49 4E 54 20 22 41 22 0D`, sha `6a1c27e3…` ; `PRINT 1+2` =
`50 52 49 4E 54 20 31 2B 32 0D`, sha `cc1285cd…` — mêmes empreintes que P3-C2, donc mêmes
octets d'entrée). Le registre `CPUSP` d'entrée porte l'adresse de retour `$000104F2` =
TEXT+`$1BEE`, à savoir l'instruction suivant immédiatement le `JSR (A0)` observé : l'entrée
cible est atteinte par le call naturel, sans injection. Les octets du vecteur sélectionné
TEXT `$1E48` sont identiques E/D (sha `33e3b3dc…`, valeur `$00014608`).

Registres à l'entrée `$14608` (identiques entre les runs `output` et `steps` d'un même cas) :

| Cas | D0 | D1 | D2 | D3 | D4 | D5 | D6 | A0 | A1 | A4 | A5 | A6 | A7 | SR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E `PRINT "A"` | 00000008 | 00000009 | FFFFFFFF | 0000EB97 | 000D00DD | 00000009 | 0000024C | 00014608 | 0002824A | 00028252 | 0002824E | 00027CF8 | 0002E1F4 | 0300 |
| D `PRINT "A"` | 00000008 | 00000009 | FFFFFFFF | 0000EB97 | 000D00DD | 00000009 | 0000024C | 00014608 | 000282F6 | 000282FE | 000282FA | 00027DA4 | 0002E2A0 | 0300 |
| E `PRINT 1+2` | 0000001A | 00000009 | FFFFFFFF | 0002822D | 000D00DD | 00000009 | 0000024C | 00014608 | 0002824A | 00028264 | 0002824E | 00027CF8 | 0002E1F4 | 0300 |
| D `PRINT 1+2` | 0000001A | 00000009 | FFFFFFFF | 00028303 | 000D00DD | 00000009 | 0000024C | 00014608 | 000282F6 | 00028310 | 000282FA | 00027DA4 | 0002E2A0 | 0300 |

D0 diffère entre les deux lignes (`$08` vs `$1A`) ; c'est une donnée d'entrée de la cible
dans ces deux cas, pas une conclusion générale.

## OBSERVED — corps capturé à l'entrée, identique E/D

Les quatre runs `steps` sauvent 512 octets à `$14608` (`*-target-body.bin`) : contenu
identique dans les quatre captures (SHA-256 `078234b7432e6d611f1b216372b77a74a26cb5f0f407db0b75b7ecf299861338`).
La listing `work/p3c3/target-body-5d04.s` est la sortie brute rg-dis reproduite mot à mot :

```
rg-dis work/p3c3/e-print-a-steps/traces/e-print-a-target-body.bin --arch 68k --cpu 68000 --org 0x14608 \
  --quiet --no-annotate-gfa --no-smart-labels -o /tmp/c3-raw-e.s   # exit 0 ; diff = 0
```

Premiers éléments structurels du listing (décodage rg-dis, offsets TEXT) :
- `$5D04` : `CLR.B $1C2(A6)` ; ensuite une chaîne de comparaisons sur des octets de token en
  `(A5)` : `CMP.B #89/#70/#33/#34/#87/#161/#162/#163` avec branches vers des blocs dédiés.
- Le bloc `$5DAE` (`_L00AE` dans le listing) avance un compteur `$1C2(A6)`, lit un format
  via `$20F2(A6)` et `A0 = A6+$7C6 + format`, et produit des octets d'espacement.
- Chemin de sortie `$5E26..$5E3C` : boucle `MOVE.B (A3)+,D0 ; MOVE.W D0,-(A7) ; MOVE.W D6,-(A7) ;
  MOVE.W #3,-(A7) ; TRAP #13 ; ADDQ.L #6,A7` — BIOS **Bconout**, D6 comme numéro de
  périphérique. Un chemin voisin `$5E44` empile buf/compte/handle `-1` et fait `TRAP #1`
  GEMDOS **Fwrite** (64).

## OBSERVED — frontière de sortie naturelle

Dans les quatre runs `output`, la continuation naturelle atteint TEXT+`$5E36` (`$1473A`,
l'`ADDQ.L #6,A7` qui suit immédiatement le `TRAP #13`) : registres E/D identiques à cet
instant, D0=`$00000001`, D6=`$00000002` (périphérique 2 = console), et la capture de pile
`*-output-stack-a7.bin` (32 octets en A7, mêmes octets a priori en USP) contient le mot
caractère `$0041` (`A`) ou `$0033` (`3`) et la chaîne de retours
`$00011070` → `$00014650` (BSR interne au corps, TEXT+`$5D4C`) → `$000104F2` (retour du
`JSR (A0)` du dispatcher). L'empreinte de cette capture ne diffère E/D que par l'absence de
toute différence : les quatre dumps sont identiques deux à deux par cas
(sha `5c7f2eb8…` pour `PRINT "A"`, `08736cd6…` pour `PRINT 1+2`). Les écrans
`screenshots/after-input.png` des runs `output` montrent `A` puis `OK >` et `3` puis `OK >`,
E comme D (observation visuelle, pas d'OCR).

**HYPOTHESIS (non nommée)** : le corps `$5D04` écrit les caractères du résultat via Bconout
sur le périphérique 2 pour ces deux lignes. Le rôle général de la routine (handler PRINT,
écrivain de sortie formatée, etc.) n'est pas établi.

## Falsifié — l'historique single-step borné n'est pas atteint

**FALSIFIED.** Ni `run_target_case.py` mode `steps` (breakpoint d'entrée avec
`:once :file entry.ini`) ni `run_steps2.py` (breakpoint `:once` simple, commandes par FIFO)
n'ont produit un historique d'instructions de la cible : dans les deux cas l'émulateur a
repris et terminé le `PRINT` avant le premier pas (`hatari-debug.log` affiche la sortie
invitée `A`/`3` et `OK >` avant le premier `c 1`, le VBL passe de 485 à 557/619, et le
`cpureg` joint montre la boucle oisive dans le ROM `$E00DB8` avec A7 en pile superviseur
`$00005756/5758`). La liste des 149 PC des runs `steps` est donc celle de la boucle d'attente
de l'interpréteur après la ligne, pas du corps cible : conservée comme échec enregistré,
non comme preuve d'exécution. **UNMEASURED :** l'ordre dynamique réel des instructions du
corps depuis l'entrée ; quels blocs du listing sont atteints pour chaque ligne ; l'arbre
d'appels interne ; la sémantique des champs A6+`$1C2`, `$7C6`, `$20F2`, `$20AE/$20B0/$20B2`.

## Contrôles

1. Mêmes octets d'entrée que P3-C2 : empreintes parser `6a1c27e3…` / `cc1285cd…` retrouvées
   sur les huit runs (steps et output, E et D).
2. Le corps capturé est identique E/D — cohérent avec le même offset TEXT relatif
   sélectionné par le même vecteur relocalisé.
3. La frontière est atteinte par continuation purement naturelle dans les quatre runs
   `output` ; aucune commande d'écriture debugger n'est exécutée (`cpureg`/`savebin`
   uniquement).
4. L'adresse de retour `$104F2` en tête de pile d'entrée prouve le chemin `JSR (A0)` observé
   en C2, sans branchement simulé.

## Reproduction et preuves brutes

Commande type (par cas, E ci-dessous) :
`python3 work/p3c3/run_target_case.py e print-a output` puis `python3 work/p3c3/run_target_case.py e print-a steps`.
Le conducteur `run_target_case.py` (sha `6c374d3c…`) fixe la chaîne de breakpoints
launch→after-pexec→after-entry→parser→dispatch→target→entry→(output) ; les fixtures `.ini`
générées et tous les binaires/logs/captures sont sous `work/p3c3/` (ignorés, hashes dans
`NATURAL_EXECUTION_36_C3_DATA.json`). `run_steps2.py` (sha `5b5439f9…`) est le correctif
tenté et également falsifié. Le listing rg-dis reproduit est `work/p3c3/target-body-5d04.s`
(sha `3d5254c2…`).

## Comparaison E/D

| Mesure | E | D | Conclusion |
|---|---|---|---|
| Entrée cible naturelle sur les 2 lignes | 2/2 | 2/2 | même adresse `$14608` |
| Corps 512 octets à l'entrée | sha `078234b7…` | sha `078234b7…` | identique |
| Frontière Bconout `$5E36` atteinte | 2/2 | 2/2 | registres E/D identiques |
| Octets de pile à la frontière | par cas identiques E/D | idem | mêmes caractères et retours |
| Sortie visible | `A`, `3` | `A`, `3` | confirmée |

## Limites et transfert

- Aucune instruction du corps n'est observée individuellement en exécution (single-step non
  abouti, voir Falsifié) ; le lien corps↔sortie est établi par l'entrée, la frontière, la
  pile de retours et la capture statique du corps, pour ces deux lignes seulement.
- Pas d'autres commandes, pas d'autres entrées, pas d'autre ROM/machine.
- P3-C reste **INCOMPLETE** : `$12EF6` et les tables P3-B toujours non observées ; la cible
  n'est pas nommée. Prochaine borne possible (non commencée) : pas-à-pas par trace
  `:trace :once` chaînée instruction par instruction, ou watchpoints en lecture sur les
  champs de format du corps.
