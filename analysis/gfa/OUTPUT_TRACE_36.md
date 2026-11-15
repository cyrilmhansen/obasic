# P3-D/2 — trace CPU naturelle et bornée de `PRINT`

## Question et méthode

**OBSERVED:** obtenir l'ordre des instructions 68000 exécutées entre TEXT `$5D04`
(runtime `$14608`, base TEXT observée `$E904`) et la frontière TEXT `$5E36`
(runtime `$1473A`) pour les quatre couples E/D × chaîne/nombre.

La méthode suit la documentation officielle Hatari 2.6.1 (`/usr/share/doc/hatari/debugger.html`, sections *Breakpoints*, *Chaining breakpoints* et *Tracing*):
`trace cpu_disasm` est activé par un breakpoint naturel
`:trace :once :file` à `$14608`; un second breakpoint identique à `$1473A`
exécute `trace none` et `b all`. Le fichier local est fourni au démarrage par
`--trace-file`. Aucun FIFO de single-step, `memwrite`, écriture de registre ou
injection d'état n'est utilisé.

Binaries: E `d44ca139e6712fd26c14abdf1d4480120a137b70919e1b9ac1c7813a532b4c39`, D
`b7706b9f9789c7ac3a9e06ded26aab55521e0c2552d2c51348ee0b87779adf6e`.
Hatari v2.6.1, binaire host SHA-256 `98d3879baf70b6e140071994ebebd791b148f72b9115c1dc512865123d0faa77`;
TOS TT SHA-256 `974211d0f3db3d81af2d5c564df2e329fec48bb359a8b1eae9edacc9bbda7816`.

## Prototype obligatoire

**OBSERVED — réussi:** E, `PRINT "A"` atteint naturellement `$14608`; le journal
débogueur montre l'exécution de `activate.ini`, l'activation effective de
`trace cpu_disasm`, puis le breakpoint `$1473A` et `deactivate.ini`. La trace
commence par `00014608 422e 01c2` et contient des instructions successives du
corps, dont les appels internes et le chargement de `$41` avant le `TRAP #13`.
Le fichier écran contient `A` puis `OK >`.

Les snapshots RAM ont été lus par `savebin` seulement. La routine de conduite ne
contient aucune opération d'écriture mémoire; le corps de code capturé à l'entrée
et à la frontière conserve le même SHA-256. Les différences de RAM générale sont
les écritures normales de l'exécution et ne sont pas présentées comme une absence
de mutations du programme invité.

## Résultats des quatre runs

**OBSERVED:** les quatre traces commencent à `$14608`, s'arrêtent juste avant
l'instruction frontière `$1473A` (dernière instruction enregistrée `$14738`, le
`TRAP #13`), et le journal confirme la désactivation par `trace none`.

| cas | instructions CPU | branches T/F | appels/retours détectés | RAM modifiée entrée→frontière* |
|---|---:|---:|---:|---:|
| E `PRINT "A"` | 363 | 11 / 42 | 28 | 138 octets |
| D `PRINT "A"` | 363 | 11 / 42 | 28 | 137 octets |
| E `PRINT 1+2` | 979 | 67 / 76 | 80 | 167 octets |
| D `PRINT 1+2` | 979 | 67 / 76 | 80 | 167 octets |

\* Le nombre de différences RAM est un contrôle de l'activité naturelle, pas une
preuve d'absence d'écriture invitée. Le SHA-256 de la fenêtre code
`$14608..$14807` est inchangé entrée/frontière dans les quatre cas.

**OBSERVED:** les listes de PC des versions E et D sont identiques pour chaque
fixture. Les chemins chaîne et nombre divergent nettement: le nombre emprunte
un chemin plus long avec davantage d'appels et de branches. Les branches sont
étiquetées T/F lorsque Hatari les imprime; les cibles et les PC successifs sont
conservés dans `OUTPUT_TRACE_36_DATA.json`.

**OBSERVED:** le journal CPU place avant la frontière:

- chaîne: `move.b (a3)+,d0` avec `$41`, puis empilement de `D0.w`, `D6.w` et `3.w`;
- nombre: `move.b (a3)+,d0` avec `$33`, puis le même empilement;
- dans les quatre cas, `D6=2` et la prochaine instruction est `TRAP #13` à
  `$14738`, donc la frontière `$1473A` est bien le retour post-Bconout mesuré
  par P3-D/1.

L'écran final montre `A` ou `3`, puis `OK >`. Les traces ne fournissent pas de
valeurs supplémentaires de workspace à inventer.

## Blocs et reconstruction

**INFERRED:** les entrées de blocs de base produites par l'analyseur sont les PC
non linéaires après retours, branches ou transferts. Elles décrivent les blocs
empruntés dans cette trace, sans transformer les annotations `rg-dis` en noms de
routines. Les appels/retours sont des motifs d'instructions (`BSR/JSR/JMP/RTS`)
et non une preuve de sémantique générale.

La comparaison avec `analysis/gfa/OUTPUT_36.md` confirme le chemin Bconout déjà
borné et apporte l'ordre dynamique. Elle distingue maintenant un chemin de
formatage chaîne plus court et un chemin numérique plus long. Elle ne mesure
 toujours pas le chemin Fwrite (`TRAP #1`, fonction 64) ni une routine générale
nommée. `$FFFD` reste un handle statique voisin; aucun rôle nouveau n'est
inféré. Toute interprétation de `$FFFD` comme valeur signée doit respecter
`$FFFD = -3` en entier signé 16 bits, pas `-1`.

## Falsification et limites

L'hypothèse testée était que les breakpoints chaînés documentés avec trace CPU
permettraient de suivre le corps sans single-step. Elle est **CONFIRMÉE pour ces
fixtures**: entrée, instructions successives, frontière et résultat visible sont
reproduits. Les anciennes tentatives FIFO restent falsifiées comme méthode et ne
sont pas utilisées ici.

**UNMEASURED:** la trace ne suffit pas à attribuer une sémantique complète aux
blocs, aux champs de workspace ou au choix Fwrite. Les valeurs de registres non
imprimées par le journal ne sont pas reconstruites.

## Reproduction

```text
python3 tools/p3d2_trace.py e print-a
python3 tools/p3d2_trace.py e print-1plus2
python3 tools/p3d2_trace.py d print-a
python3 tools/p3d2_trace.py d print-1plus2 --tag retry2
python3 tools/p3d2_analyze.py
```

Le conducteur et l'analyseur sont `tools/p3d2_trace.py` et
`tools/p3d2_analyze.py`. Les journaux bruts, snapshots RAM et écrans sont sous
`work/p3d2/`; le run D numérique canonique est `work/p3d2/d-print-1plus2-retry2/`.
Le premier essai D numérique est conservé séparément comme échec de temporisation
d'entrée, sans être utilisé comme preuve scientifique.
