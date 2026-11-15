# P3-C3 handoff — corps cible TEXT $5D04 borné à la frontière de sortie

## Résultat

Les deux lignes `PRINT "A"` et `PRINT 1+2` atteignent naturellement la cible `$14608`
(TEXT `$5D04`, base `$E904`) sous E et D avec les octets exacts de P3-C2 ; la pile d'entrée
porte l'adresse de retour `$104F2` = TEXT+`$1BEE`, preuve du `JSR (A0)` observé en C2. Le
corps a été capturé (512 octets identiques dans les quatre runs et E/D, sha
`078234b7…`) et désassemblé par rg-dis 0.11.46 reproductible mot à mot ; la structure
(boucle sur les tokens en `(A5)`, compteur A6+`$1C2`, format A6+`$20F2`/`$7C6`, boucle
Bconout `TRAP #13` périphérique 2, successeur Fwrite handle `-1`) est documentée. La
frontière de sortie naturelle est atteinte : continuation pure jusqu'à TEXT+`$5E36`
(à peine après le Bconout), capture de pile contenant le caractère affiché (`$41`/`$33`)
et la chaîne de retours `$11070→$14650→$104F2`, écrans `A`/`3` puis `OK >` sous E et D.

Échec enregistré : le single-step borné du corps n'a pas fonctionné (deux méthodes,
`run_target_case.py steps` et `run_steps2.py`) — Hatari reprend l'émulation avant le
premier pas, la liste des 149 PC est la boucle oisive post-ligne. L'ordre dynamique
d'exécution du corps reste **UNMEASURED** ; P3-C reste **INCOMPLETE** (scanner `$12EF6`,
tables P3-B, nommage de la cible toujours ouverts).

## Preuves

- Rapport, limites, commande de reproduction : [NATURAL_EXECUTION_36_C3.md](NATURAL_EXECUTION_36_C3.md).
- Registres, octets, empreintes des 150 fichiers bruts : [NATURAL_EXECUTION_36_C3_DATA.json](NATURAL_EXECUTION_36_C3_DATA.json).
- Artefacts bruts (logs debugger, binaires, captures écran, conducteurs) : `work/p3c3/`, non versionnés.
- Base amont : P3-C2 `NATURAL_EXECUTION_36_C2.md` et son JSON ; profil `tools/hatari_gfa_scancode.cfg`.

## Recommandation suivante (non commencée)

Si le pas-à-pas du corps redevient prioritaire : chaîne de breakpoints `:trace :once`
instruction par instruction (sans jamais drop interactif), ou watchpoints en lecture sur
les champs de format du corps pendant la continuation naturelle — sinon enchaîner sur la
question suivante de P3-D en gardant la cible non nommée.
