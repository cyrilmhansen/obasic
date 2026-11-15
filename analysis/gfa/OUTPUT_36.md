# P3-D/1 — chemin de sortie naturel de `PRINT`

## Question et périmètre

Reconstruire, sans nommer prématurément la cible TEXT `$5D04`, le sous-chemin effectivement
emprunté par `PRINT "A"` et `PRINT 1+2` sous GFA 3.6 E et 3.6TT D. Les affirmations
ci-dessous sont limitées aux quatre exécutions naturelles P3-C3; elles ne généralisent ni
la routine ni l'équivalence E/D.

Binaries: E `d44ca139e6712fd26c14abdf1d4480120a137b70919e1b9ac1c7813a532b4c39`, D
`b7706b9f9789c7ac3a9e06ded26aab55521e0c2552d2c51348ee0b87779adf6e`. Hatari 2.6.1
sha `98d3879baf70b6e140071994ebebd791b148f72b9115c1dc512865123d0faa77`; rg-dis 0.11.46
sha `1a66448a2a3215ded9e89515f3e0c5fbb02e7d05ec9e8bc175dda492734bc4ef`; ROM sha
`974211d0f3db3d81af2d5c564df2e329fec48bb359a8b1eae9edacc9bbda7816`.

## Graphe statique candidat

Source immutable: `work/p3c3/target-body-5d04.s`, 512 octets à runtime `$14608`,
TEXT `$5D04`; empreinte `078234b7432e6d611f1b216372b77a74a26cb5f0f407db0b75b7ecf299861338`.
La conversion des offsets runtime en offsets TEXT utilise la base observée `$E904`.

| Bloc TEXT | Transferts statiques décodés | Statut |
|---|---|---|
| `$5D04..$5D4A` | `CLR.B $1C2(A6)`; tests de token; branches vers `$5D50`, `$5D64`, `$5D6E`, `$5D8A`, `$5DAE`; boucle retour vers `$5D0E` | code candidat; branchement dynamique non observé |
| `$5D4C` | `BSR` interne observé dans la chaîne de retour (`$14650` runtime) | cible d'appel identifiée, corps non suivi |
| `$5D50..$5D63` | calcule une quantité depuis `$1C2`, `LEA` du littéral d'espaces `$5D7A`, puis `$5DAE` | code; rôle exact du compteur non prouvé |
| `$5D64..$5D89` | avance `(A5)`, teste `$46`, retourne ou revient à `$5D0E` | code candidat |
| `$5D6E..$5D79` | initialise `$1C6(A6)` avec `$0D0A`, `D0=2`, puis `$5DAE` | code candidat |
| `$5D7A..$5D89` | 16 octets `$20` | données, pas instructions |
| `$5D8A..$5DAD` | avance `(A5)`, `BSR $618C`, retour `$5D0E` | code candidat; appel opaque |
| `$5D94..$5DAC` | conversions via `BSR` opaques, résultat dans `D0` | code candidat; appels non résolus |
| `$5DAE..$5E12` | met à jour `$1C2`; lit `$20F2`; indexe `$7C6`; boucle `DBRA`/règles CR/BS; écrit le format | code; accès champs identifiés, sémantique non établie |
| `$5E12..$5E24` | lit `$20F2`; branche selon signe; tests `$20B2`; certains `BEQ.W` ont des cibles hors capture | code + transferts hors fenêtre; destinations non attribuées |
| `$5E24..$5E3C` | sauvegarde A3; boucle octets; empile caractère, D6, `#3`; `TRAP #13`; dépile 6 octets | code Bconout; route observée pour les deux fixtures |
| `$5E44..$5E58` | empile buffer, compte, handle `$FFFD`, `#64`; `TRAP #1`; nettoie 12 octets | code Fwrite; présence statique seulement |
| `$5E58..` | branche hors fenêtre / accès `$20B2`; `BSR $5DAE` | code candidat; non suivi dynamiquement |
| `$5E??..$5F04` | conversions/formatage et écritures `$14F0`, `$15F0`, `$8D0`; `dc.w` et cibles hors capture | mélange code candidat et zones indéterminées; ne pas interpréter comme chemin mesuré |

Les mots `dc.w` restent ambigus sans vérification indépendante de leurs cibles: ils ne
sont pas utilisés pour inventer une sémantique. Les appels immédiats sont cartographiés
comme `BSR` vers `$5D4C`, `$5D94`, `$5DA4`, `$5D8A`, `$5F??` et les cibles hors fenêtre;
leurs corps ne sont pas compris dans P3-D/1.

## Traces naturelles par blocs

**OBSERVED (P3-C3):** quatre entrées naturelles atteignent `$14608`; la pile porte le
retour `$104F2` (instruction après `JSR (A0)`). Les quatre continuations naturelles
atteignent `$1473A` = TEXT `$5E36`, immédiatement après `TRAP #13`; D0=`$1`, D6=`$2`.
La pile contient `$0041` pour `PRINT "A"`, `$0033` pour `PRINT 1+2`, puis la chaîne de
retours `$11070 → $14650 → $104F2`. Les écrans montrent `A`/`3`, puis `OK >`, sous E et D.

**UNMEASURED:** aucun PC intermédiaire du corps n'est établi par une trace ordonnée. La
tentative P3-D/1 `work/p3d1/run_block_trace.py` a posé des breakpoints candidats, mais
le premier événement utile est resté l'entrée `$5D04`; aucun fichier de bloc ultérieur
n'a été produit avant la fin/fermeture de la fenêtre. Ce résultat négatif est conservé;
il ne transforme pas les breakpoints non atteints en preuve d'inexécution.

Ainsi, la succession `$5D04 → ... → $5E36` est une **borne d'entrée/sortie**, pas un
ordre de blocs observé. Les champs A6+`$1C2`, `$7C6`, `$20F2` sont lus/écrits statiquement;
leurs valeurs intermédiaires n'ont pas été capturées.

## Interprétation limitée des sorties

**INFERRED, appuyé par statique + frontière naturelle:** le sous-chemin Bconout prépare un
caractère dans `D0`, empile `D0.w`, `D6.w` et `3.w`, exécute BIOS `Bconout` (`TRAP #13`),
puis retire 6 octets. Pour les deux fixtures, le périphérique est la console (`D6=2`) et
le caractère est `$41` ou `$33`.

**OBSERVED statique seulement:** un chemin voisin empile buffer/compte/handle `$FFFD`,
exécute GEMDOS `Fwrite` (`TRAP #1`, fonction 64), puis retire 12 octets. Aucun de ces deux
runs ne prouve que Fwrite est sélectionné.

## Falsification

Hypothèse testée: les essais de single-step et de breakpoints chaînés permettraient de
mesurer l'ordre dynamique. **FALSIFIED comme méthode dans ce profil:** Hatari reprend
l'émulation après la chaîne `:file`; P3-C3 observe déjà la sortie et la boucle idle avant
le premier `c 1`. P3-D/1 a conservé le même échec pratique avec les breakpoints candidats.
Aucune fixture supplémentaire n'a été ajoutée: les fixtures existantes distinguent déjà
les caractères `$41`/`$33` et la frontière Bconout, mais pas les blocs internes; ajouter une
entrée sans instrumentation fiable n'aurait pas ce pouvoir discriminant.

## Reconstruction et limites

`reconstruction/gfa-3.6/output/output.c` conserve les opérations 68000 pertinentes,
les champs, piles et deux formes d'appel système. Il sépare les appels opaques et ne
nomme pas `$5D04` « handler PRINT ». La reconstruction est partielle et historiquement
traçable, non une implémentation équivalente.

## Reproduction / preuves

- `python3 work/p3c3/run_target_case.py {e,d} {print-a,print-1plus2} output` — exit 0 dans P3-C3; traces et hashes dans `NATURAL_EXECUTION_36_C3_DATA.json`.
- `python3 work/p3d1/run_block_trace.py e print-a` — tentative P3-D/1; échec de capture intermédiaire, artefacts sous `work/p3d1/`.
- `rg-dis work/p3c3/e-print-a-steps/traces/e-print-a-target-body.bin --arch 68k --cpu 68000 --org 0x14608 --quiet --no-annotate-gfa --no-smart-labels` — exit 0, listing reproduite byte-exact.
- `make test` — exit 0, 25 tests.
- `git diff --check` — exit 0 avant livrables.

## Divergences E/D et questions ouvertes

Aucune divergence mesurée dans les quatre frontières de sortie, les corps de 512 octets,
les caractères ou le périphérique. Les registres d'entrée A1/A5/A6/A7 et D3 diffèrent
par relocalisation/état de frame, comme documenté en C3; cela ne prouve pas l'équivalence.
Restent ouverts: ordre des blocs, sens général de la cible, valeurs des champs pendant
l'exécution, choix Fwrite, appels hors fenêtre, scanner `$12EF6` et tables P3-B.
