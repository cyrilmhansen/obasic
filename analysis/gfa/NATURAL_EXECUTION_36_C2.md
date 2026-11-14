# P3-C2 — Saisie clavier déterministe et premier BASIC exécuté

## Question et résultat

Cette phase vérifie si des instructions entrées au clavier en mode direct peuvent atteindre le parser avec les octets voulus, être acceptées par les interpréteurs E et D, puis produire une trace de dispatch et une sortie visible.

**OBSERVED — réussite limitée à ces cas :** `PRINT`, `PRINT "A"` et `PRINT 1+2` ont été saisis par le clavier de l'interpréteur, capturés exactement au point d'entrée parser, acceptés sous les deux exécutables, et suivis jusqu'au dispatch. L'écran montre respectivement une ligne vide, `A` et `3`. Pour chacun, E et D ont sélectionné la même cible runtime `$14608` depuis le point d'appel indirect. Cela établit un premier chemin naturel jusqu'à une cible appelée, mais ne démontre ni l'équivalence générale des interpréteurs ni le rôle général de cette routine.

**P3-C reste INCOMPLETE.** Les expériences C2 ferment le blocage de saisie et fournissent un oracle limité à trois formes PRINT. Elles ne mesurent pas toutes les étapes du parser, les tables P3-B, ni le comportement de l'ensemble du langage.

## Artéfacts et profil contrôlé

| Élément | Valeur |
|---|---|
| Hatari | 2.6.1 |
| Machine | Atari TT |
| ROM | TOS 3.06 TT, image `work/p3b/roms/tos306-tt-gb.img`, locale `en-GB`, SHA-256 `974211d0f3db3d81af2d5c564df2e329fec48bb359a8b1eae9edacc9bbda7816` |
| GFA E | `work/extracted/p2/gfa-3.6/GFABASIC.PRG`, SHA-256 `d44ca139e6712fd26c14abdf1d4480120a137b70919e1b9ac1c7813a532b4c39` |
| GFA D | `work/extracted/p2/gfa-3.6tt/GFABASIC.PRG`, SHA-256 `b7706b9f9789c7ac3a9e06ded26aab55521e0c2552d2c51348ee0b87779adf6e` |
| Profil clavier Hatari | `tools/hatari_gfa_scancode.cfg`, `[Keyboard] nKeymapType = 1`, SHA-256 `758f98d8015eb8b1c37bfa86b458dcf421c784c97fb2aaffdb7deb69d9c79df0` |
| Mode d'entrée | Éditeur GFA historique en mode direct, activé par `Shift-F9`, puis événements clavier X11 et Return |

Les disques virtuels de travail sont séparés sous `work/p3c2/drive-e` et `work/p3c2/drive-d`. Chaque lancement utilise un `HOME` isolé et une copie de la graine NVRAM conservée sous `work/p3c/hatari-home/`; les originaux, ROM et disques acquis ne sont pas écrits. Le debugger Hatari reçoit des commandes par FIFO. `cpureg` et `savebin` ne font que lire l'état; aucun `write`, `set`, poke ou autre commande n'a fabriqué le buffer d'entrée.

## Diagnostic X11 → Hatari → clavier invité

**OBSERVED.** `file` identifie la ROM comme `1991-09-24 Video: PAL Locale: en-GB`. `setxkbmap -query` rapporte `layout: us` sous Xwayland, alors que l'inspection `xmodmap -pke` et les événements effectivement envoyés correspondent aux symboles d'une disposition hôte AZERTY : keycode 10 produit `ampersand/1`, 11 `eacute/2`, 12 `quotedbl/3`, 21 porte la touche plus/égal, et keycode 38 produit `q/Q` à la position physique de A sur AZERTY. Le résultat `setxkbmap` seul ne décrivait donc pas les symboles utilisés par cette session X11.

Hatari est configuré explicitement en **scancode**. Cela fait correspondre les positions physiques des touches hôte aux positions du clavier Atari; la ROM TOS détermine ensuite le caractère associé à cette touche selon sa disposition anglaise. Ces deux dispositions sont distinctes. L'ancien essai P3-C utilisait le mode symbolic par défaut et une chaîne X11 contenant les guillemets; la touche hôte `3` se traduisait alors par le chiffre invité `3`, donnant `PRINT 3A3`.

Séquence reproductible observée avec `xdotool` :

| Texte invité | Événements hôte X11 |
|---|---|
| `PRINT` et espace | `xdotool type --clearmodifiers --delay 90 'PRINT '` |
| `"` | `xdotool key shift+eacute` (touche physique AZERTY 2; TOS anglais produit le guillemet) |
| `A` | `xdotool key shift+q` (touche physique AZERTY A) |
| `1` | `xdotool key ampersand` (touche physique AZERTY 1, sans Shift) |
| `+` | `xdotool key plus` |
| `2` | `xdotool key eacute` (touche physique AZERTY 2, sans Shift) |
| `3` pour le contrôle négatif | `xdotool key quotedbl` (touche physique AZERTY 3, sans Shift) |
| fin de ligne | `xdotool key Return` |

`xdotool type '1'` et la méthode générale `type` sur les touches numériques ont échoué à la calibration : les événements de modification Shift ont donné des caractères invités différents, notamment `!+"` dans une tentative arithmétique exploratoire. Cette tentative est un échec enregistré, pas un résultat BASIC. La calibration retenue compare les octets ASCII au buffer capturé, et pas seulement les touches X11 envoyées.

Le contrôle volontairement erroné a remplacé `shift+eacute` par `shift+quotedbl` pour les guillemets. Le buffer obtenu contient `9C` aux deux positions au lieu de `22` et la ligne est rejetée. Ainsi, la calibration détecte un changement de touche réel.

## Points d'observation et traduction des adresses

La base TEXT observée après transfert Pexec est `$E904` dans E comme D. Les points sont donc calculés à partir de cette base, et non confondus avec des adresses absolues :

| Rôle observé | Offset TEXT | Adresse absolue de ce profil |
|---|---:|---:|
| Entrée parser appelée en mode direct | `$12DF6` | `$216FA` |
| Scanner interne candidat | `$12EF6` | `$217FA` |
| Entrée dispatcher | `$1BD6` | `$104DA` |
| Instruction `JSR (A0)` | `$1BEC` | `$104F0` |
| Entrée du vecteur observé | `$1E48` | `$1074C` |

La contradiction `$12DF6` / `$12EF6` se résout pour ces exécutions : le breakpoint `$12DF6` est atteint par les trois lignes directes; le breakpoint `$12EF6` a été armé depuis le parser et n'a été atteint pour aucune des six exécutions valides E/D. Il s'agit d'un point scanner interne distinct, pas du point d'entrée direct observé.

## Résultats des entrées et sorties

Les dumps parser de 128 octets sont enregistrés avec huit octets avant A0. Les séquences exactes après ce préfixe sont :

| Entrée | Octets ASCII incluant CR | E | D | Sortie visible |
|---|---|---|---|---|
| `PRINT` | `50 52 49 4E 54 0D` | acceptée | acceptée | ligne vide, puis prompt `OK >` |
| `PRINT "A"` | `50 52 49 4E 54 20 22 41 22 0D` | acceptée | acceptée | `A`, puis prompt `OK >` |
| `PRINT 1+2` | `50 52 49 4E 54 20 31 2B 32 0D` | acceptée | acceptée | `3`, puis prompt `OK >` |

Les captures d'écran sont conservées sous `work/p3c2/{e,d}-<cas>/screenshots/after-input.png`; les SHA-256 sont dans le JSON C2. Il s'agit d'une observation visuelle de la sortie Hatari, sans OCR. La capture de l'écran correspond à un état post-saisie où le résultat est affiché et le prompt revenu.

### Chemin de contrôle et sélection de cible

**OBSERVED.** Les six cas valides (trois lignes × E/D) atteignent `$216FA` avec leur buffer d'entrée. Ensuite les breakpoints sur `$104DA` puis `$104F0` sont déclenchés. Au call indirect, les deux variantes ont `D6=$024C`, `A0=$14608`; l'entrée `$1E48` contient à l'exécution `00 01 46 08`, c'est-à-dire le pointeur relocalisé `$00014608`. La capture de quatre octets est strictement identique en E et D (SHA-256 `33e3b3dc4cd4b04921624bbb6ae08e82b2c82399d52e05c33fdf70a42d27ccd0`). Le dump PRG initial à TEXT `$1E48` était `00 00 5D 04`; avec la base TEXT `$E904`, la valeur relative `$5D04` résout également vers `$14608`.

Pour `PRINT "A"`, les registres d'entrée du dispatcher sont E `A5=$2824A`, D6 `$46`, et D `A5=$282F6`, D6 `$46`. Au call, le cadre indique E `A5=$2824E`, D `A5=$282FA`, et dans les deux cas D6 `$24C`, A0 `$14608`. Le dump A5 commence dans les deux versions par `00 08 02 4C DE 01 41 46 00 04 00 B8 ...`; le dispatcher avance A4 par le premier mot `$0008`, prend `$024C` pour l'index de vecteur, charge le pointeur et l'appelle. L'assembleur P1/P3-B à `$1BE4` confirme les opérations `ADDA.W (A5)+,A4`, `MOVE.W (A5)+,D6`, `MOVEA.L *+16(PC,D6.W),A0`, `JSR (A0)`.

La cible runtime `$14608` correspond au même code relatif TEXT `$5D04` dans les deux versions et sa sélection est maintenant associée sans ambiguïté aux trois instructions PRINT valides : la ligne a été capturée avant son traitement, le flux naturel atteint le vecteur, le pointeur sélectionné a été lu, et l'écran montre le résultat après poursuite. **On ne nomme pas cette routine « handler PRINT » au-delà de ces cas observés**; l'exécution contrôlée a été arrêtée à l'entrée cible et n'a pas tracé son corps. Le résultat visuel provient du run continu correspondant, avec mêmes octets et configuration.

**UNMEASURED.** Le scanner `$12EF6`, la lecture de la table statique TEXT `$1111E`, et les lectures des maps générées A6+`$D2C` / A6+`$10CC` n'ont pas été observés sur les chemins directs testés. Le fait que ces points n'aient pas été atteints ne signifie pas qu'ils sont inutilisés dans d'autres modes d'entrée.

## Comparaison E/D et portée

| Mesure dans les cas couverts | E | D | Conclusion limitée |
|---|---|---|---|
| Lignes validées | 3/3 | 3/3 | mêmes trois syntaxes acceptées |
| Octets capturés au parser | 3 séquences attendues sur 3 | 3 séquences attendues sur 3 | correspondance exacte par cas |
| Entrée dispatcher `$1BD6` | 3/3 | 3/3 | tous les cas atteignent le même offset TEXT |
| `JSR (A0)` `$1BEC` | 3/3 | 3/3 | tous les cas atteignent le call indirect |
| D6 à l'appel | `$024C` pour 3/3 | `$024C` pour 3/3 | même index sur ces exemples |
| Cible A0 | `$14608` pour 3/3 | `$14608` pour 3/3 | même cible observée |
| Sortie visible | ligne vide, `A`, `3` | ligne vide, `A`, `3` | mêmes sorties dans ces cas seulement |
| Scanner `$12EF6` | 0/3 atteints | 0/3 atteints | point scanner non emprunté par ces cas directs |

Les trames parser/dispatcher/cible utiles sont byte-identiques entre E et D pour les mêmes cas quand leur adresse de départ est relative à A0/A5; les adresses de cadres absolues diffèrent avec le workspace. Les captures complètes et leurs empreintes sont dans `NATURAL_EXECUTION_36_C2_DATA.json`. Cette concordance est un résultat d'exécution de trois exemples, pas une preuve d'équivalence comportementale générale.

## Falsification et contrôle négatif

1. **Ancienne entrée invalide.** `PRINT 3A3` a été saisie normalement dans E et D, capturée comme `50 52 49 4E 54 20 33 41 33 0D`, puis rejetée (`Syntax Error` en E, `Syntax Fehler` en D). Aucun breakpoint dispatcher n'a été observé pour ce contrôle.
2. **Touche changée volontairement.** L'utilisation de `shift+quotedbl` au lieu de `shift+eacute` a produit `50 52 49 4E 54 20 9C 41 9C 0D` sous D et a été rejetée. La saisie n'est donc pas réputée correcte sur la seule foi de la séquence d'événements.
3. **Absence d'injection.** Aucune commande debugger n'a écrit le buffer ou les octets du programme; `savebin` a sauvegardé les octets que le parser recevait après les touches normales. Les buffers contiennent exactement les séquences du tableau ci-dessus.

## Reproduction et preuves brutes

Le profil clavier versionné est `tools/hatari_gfa_scancode.cfg`. Pour reproduire, préparer une copie de travail séparée du disque de chaque version dans `work/p3c2/drive-e` et `work/p3c2/drive-d`, puis, par lancement, définir un HOME temporaire de run et copier la NVRAM de référence P3-C dans ce HOME. Lancer Hatari 2.6.1 avec `--configfile tools/hatari_gfa_scancode.cfg --machine tt --tos work/p3b/roms/tos306-tt-gb.img --harddrive work/p3c2/drive-{e,d} --cmd-fifo <fifo> --parse <fixtures/launch.ini> --window --trace os_base,gemdos,keymap,nvram --trace-file <run>/traces/hatari.trace`. Le script de conduite et les fixtures Hatari générés pour les expériences sont archivés sous `work/p3c2/`; le conducteur utilisé était `work/p3c2/run_natural_case.py`. Les événements de saisie sont listés dans la section clavier ci-dessus.

À partir de la trace de Pexec, confirmer TEXT `$E904`, armer `$12DF6`; au passage parser sauvegarder `a0-8` sur 128 octets et armer `$12EF6` et `$1BD6`; au dispatcher sauvegarder A5 sur 64 octets et armer `$1BEC`; au call enregistrer les registres, A5, et les 4 octets à `TEXT+$1E48`. Continuer le run jusqu'au retour au prompt puis capturer la fenêtre Hatari. Ces opérations de preuve sont en lecture seule.

Principales preuves sous `work/p3c2/` :

| Cas | Capture parser SHA-256 (identique E/D) | Captures dispatch/cible et écran |
|---|---|---|
| `PRINT` | `0ba02295efa2ac2293428b45b98b62d52ba409fbd5001a0daa2b0dc702853569` | fichiers et empreintes dans JSON, `d-print-empty/`, `e-print-empty/` |
| `PRINT "A"` | `6a1c27e3dd248ea7e82959e6ca4f6fe0d6a2c937d31fde24091dd503db0db5c6` | vecteur, cadres et captures écran E/D dans JSON |
| `PRINT 1+2` | `cc1285cdbe648388661a55479a1f86c4248ba8f8f399c70f5ad2a09b2db680d4` | vecteur et captures écran E/D dans JSON |
| négatif `PRINT 3A3` | `f1b580714adb0cf42e07b1131b330e5147b6eacd6e0410f7144dbb53e1a100a1` | rejet E/D; aucun dispatch |
| mauvaise touche | `84f4ad3a07d3dd350fccde62679417d42f6b2a78690d66354c4473a8daad08db` | rejet D; écran dans JSON |

Les fichiers binaires/captures sont exclus de Git et restent sous `work/`. Le JSON C2 porte les versions, hashes, octets, registres, transitions et empreintes des fichiers correspondants.

## Limites et transfert

- Les sorties sont démontrées pour `PRINT`, `PRINT "A"` et `PRINT 1+2` seulement; `PRINT` seul confirme le mode direct et le retour prompt, pas une sortie utile.
- L'arrêt au call indirect ne suit pas le corps de la cible; sa sélection est prouvée par l'instruction `JSR`, le pointeur vectoriel et les mêmes runs validés, sans attribuer de nom fonctionnel au code cible.
- Le scanner `$12EF6` et les trois tables P3-B ne sont pas lus de façon confirmée dans ces chemins.
- Le contrôle négatif de mauvaise touche a été fait sous D; l'ancien `PRINT 3A3` a été reproduit sous E et D.
- Pas d'exécution sur TOS français ou autre matériel; les conclusions sont pour Hatari TT 2.6.1 et l'image TOS identifiée.

La prochaine étape peut être limitée au corps à TEXT `$5D04` (adresse runtime `$14608` dans ce profil), en comparant les données d'entrée et la sortie de `PRINT "A"` puis `PRINT 1+2`. Il faudra suivre les appels système/vidéo et laisser les tables du scanner comme question distincte, à rouvrir seulement si de nouvelles traces montrent leur usage.
