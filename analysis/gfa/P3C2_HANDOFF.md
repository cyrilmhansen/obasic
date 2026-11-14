# P3-C2 handoff — entrée directe et première exécution BASIC

## Résultat

La calibration clavier est close pour cette configuration : Hatari 2.6.1, Atari TT, ROM Atari TOS 3.06 TT en-GB, profil clavier Hatari scancode et session X11 dont les symboles observés sont AZERTY. Les événements adaptés ont livré des octets exacts au parser pour trois lignes saisies au clavier en mode direct : `PRINT`, `PRINT "A"` et `PRINT 1+2`.

E et D ont accepté les trois lignes, atteint le dispatcher TEXT `$1BD6`, puis exécuté le call indirect à `$1BEC` avec D6 `$024C` et A0 `$14608`. L'entrée de vecteur TEXT `$1E48` était `$00014608` après relocation pour `PRINT "A"`. Les écrans montrent la ligne vide, `A` et `3` selon les cas. La correspondance est mesurée uniquement pour ces exemples.

P3-C reste **INCOMPLETE** : la cible n'est pas nommée fonctionnellement en dehors de ce que ces contrôles prouvent, le corps n'a pas été suivi, et ni `$12EF6` ni les accès aux tables P3-B n'ont été observés sur les parcours directs retenus.

## Preuves

- Analyse, méthodologie, limites et commandes : [NATURAL_EXECUTION_36_C2.md](NATURAL_EXECUTION_36_C2.md).
- Résultats structurés, registres, octets et SHA-256 : [NATURAL_EXECUTION_36_C2_DATA.json](NATURAL_EXECUTION_36_C2_DATA.json).
- Profil Hatari versionné : `tools/hatari_gfa_scancode.cfg`.
- Captures brutes et copies des environnements : `work/p3c2/` (non versionnés).

Le mauvais mapping est falsifié par deux contrôles : l'ancienne ligne `PRINT 3A3` est encore rejetée sous E/D; la touche de guillemet volontairement changée donne `9C` dans le buffer et est rejetée sous D. Ces contrôles montrent que l'exactitude est vérifiée au buffer parser et non déduite des événements clavier.

## Recommandation P3-C3 / P3-D

Fermer le reste de P3-C en ajoutant des watchpoints en lecture sur TEXT `$1111E`, A6+`$D2C` et A6+`$10CC` lors de ces entrées normales, si l'objectif table/parser reste prioritaire. En parallèle, borner P3-D au code entrant à TEXT `$5D04` (adresse `$14608` dans le profil observé) : poursuivre `PRINT "A"` et `PRINT 1+2` jusqu'aux appels de sortie et comparer les flux d'octets/formatages E/D. Ne pas extrapoler ces comportements à d'autres commandes ni considérer `$14608` comme un handler globalement identifié.
