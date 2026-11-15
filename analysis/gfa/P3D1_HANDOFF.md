# P3-D/1 handoff — chemin de sortie borné

## Résultat

P3-D/1 produit une reconstruction partielle du chemin de sortie atteint naturellement
par `PRINT "A"` et `PRINT 1+2`, sous GFA 3.6 E et 3.6TT D. Les deux entrées atteignent
TEXT `$5D04` / runtime `$14608`; les quatre runs atteignent TEXT `$5E36`, immédiatement
après le `TRAP #13` Bconout. À cette frontière D0 vaut `$1`, D6 vaut `$2`, et les captures
de pile contiennent `$41` ou `$33` avec la chaîne `$11070→$14650→$104F2`.

Le désassemblage statique identifie une boucle de préparation autour de `$1C2(A6)`,
`$7C6(A6)` et `$20F2(A6)`, un chemin Bconout (`#3`, `TRAP #13`) et un chemin voisin
Fwrite (`#64`, `TRAP #1`, handle `$FFFD`). Seul le chemin Bconout est relié à l'exécution
naturelle des deux fixtures. `$5D04` n'est pas nommé « handler PRINT ».

## Limites

L'ordre dynamique des blocs, les valeurs intermédiaires des champs, l'arbre d'appels,
la sélection Fwrite et la sémantique générale restent UNMEASURED. Le single-step et la
pose de breakpoints candidats en chaîne n'ont pas produit de trace intermédiaire fiable;
les logs et le conducteur sont conservés sous `work/p3d1/`. Aucune fixture supplémentaire
n'a été exécutée car les deux cas existants distinguent déjà les caractères mais pas les
blocs, et l'instrumentation disponible ne mesure pas leur ordre.

## Livrables et contrôles

- `analysis/gfa/OUTPUT_36.md`
- `analysis/gfa/OUTPUT_36_DATA.json`
- `reconstruction/gfa-3.6/output/output.c` et `README.md`
- `work/p3d1/run_block_trace.py` et sorties brutes
- `make test`: 25 tests OK
- `git diff --check`: OK avant clôture

## Next action

**P3-D/1 est terminé avec limites explicites.** Pour poursuivre, obtenir une
instrumentation Hatari capable de suspendre/reprendre naturellement à chaque bloc, puis
mesurer l'ordre et les champs; ne pas compléter la reconstruction par inférence.
