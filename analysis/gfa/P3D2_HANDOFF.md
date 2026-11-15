# P3-D/2 handoff — trace CPU naturelle bornée

## Résultat

P3-D/2 est réussi sur le prototype E `PRINT "A"`, puis sur E/D × chaîne/nombre.
La combinaison documentée Hatari 2.6.1 `trace cpu_disasm` + breakpoints
`:trace :once :file`, activée naturellement à runtime `$14608` et désactivée à
`$1473A`, fournit des PC successifs du corps jusqu'au `TRAP #13` à `$14738`.
Les quatre écrans conservent la sortie attendue (`A` ou `3`, puis `OK >`).

Les chemins E et D ont les mêmes listes de PC pour chaque fixture. La chaîne
contient 363 instructions CPU enregistrées; le nombre en contient 979. Le chemin
numérique prend donc un chemin plus long et plus d'appels/branches observés.
La fenêtre code `$14608..$14807` reste identique entre les snapshots d'entrée et
de frontière. Les mutations RAM générales sont celles de l'exécution naturelle;
le conducteur n'injecte ni écritures mémoire ni registres.

## Livrables

- `analysis/gfa/OUTPUT_TRACE_36.md`
- `analysis/gfa/OUTPUT_TRACE_36_DATA.json`
- `tools/p3d2_trace.py`
- `tools/p3d2_analyze.py`
- traces brutes sous `work/p3d2/`

## Limites

Les PC, branches T/F et motifs d'appels/retours sont observés. Les blocs de base
sont une dérivation mécanique des transferts observés. La sémantique générale,
les valeurs de workspace non journalisées et le chemin Fwrite restent
UNMEASURED. `$FFFD` n'est pas réinterprété: en signé 16 bits il vaut -3.

## Vérifications à effectuer avant clôture

`make test`, validation JSON, `git diff --check`, puis commit local des seuls
livrables P3-D/2. Ne pas modifier `artifacts/sources.json`, ne pas pousser et ne
pas modifier la politique Handoff.

## Next action

**Clôturer P3-D/2 après vérification automatisée, commit local et finalisation du
checkpoint; conserver le chemin Fwrite comme UNMEASURED.**
