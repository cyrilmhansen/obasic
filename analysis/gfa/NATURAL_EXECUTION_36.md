# P3-C — première tentative d’exécution naturelle (GFA 3.6 E / 3.6TT D)

## Question et verdict

Cette expérience devait suivre une instruction BASIC saisie normalement depuis l’éditeur jusqu’au handler, puis observer son résultat. **Le critère d’acceptation n’est pas atteint.** Les deux interpréteurs ont reçu une ligne par clavier invité, mais le mapping clavier français de TOS/Hatari a transformé la saisie voulue `PRINT "A"` en octets `PRINT 3A3` (sans délimiteur de chaîne valide). E et D ont rejeté cette entrée. Aucun résultat `A` ou `3` n’a été observé. Le passage d’un dispatcher capturé en D ne peut pas être attribué de façon fiable à une instruction valide.

Ce rapport conserve donc un résultat négatif reproductible, pas une démonstration parser → handler d’une instruction BASIC acceptée.

## Artéfacts et profil

| Élément | Valeur observée |
|---|---|
| Interpréteur E | `work/extracted/p2/gfa-3.6/GFABASIC.PRG`, SHA-256 `d44ca139e6712fd26c14abdf1d4480120a137b70919e1b9ac1c7813a532b4c39` |
| Interpréteur D | `work/extracted/p2/gfa-3.6tt/GFABASIC.PRG`, SHA-256 `b7706b9f9789c7ac3a9e06ded26aab55521e0c2552d2c51348ee0b87779adf6e` |
| ROM | TOS 3.06 TT, `work/p3b/roms/tos306-tt-gb.img`, SHA-256 `974211d0f3db3d81af2d5c564df2e329fec48bb359a8b1eae9edacc9bbda7816` |
| Émulateur | Hatari 2.6.1, machine `tt`, `--trace os_base,gemdos`; même ROM et options pour E/D |
| Base TEXT constatée | `$E904` dans les deux processus. Elle a été lue au breakpoint suivant Pexec; ce n’est pas l’adresse de base du fichier PRG. |

Les empreintes des PRG et les tailles TEXT/DATA/BSS proviennent de l’inventaire P1/P2 et ont été recalculées avant l’expérience. Les fichiers originaux n’ont pas été modifiés. Les copies des disques virtuels sont isolées sous `work/p3c/drive-d/` et `work/p3c/drive-e/`.

### Adresses absolues sous ce profil

| Point | Offset TEXT | Adresse Hatari observée/calculée depuis TEXT `$E904` |
|---|---:|---:|
| Entrée parser appelée par la boucle interactive | `$12DF6` | `$216FA` |
| Scanner interne, branche vers la table statique | `$12EF6` | `$217FA` |
| Entrée dispatcher | `$1BD6` | `$104DA` |
| `JSR (A0)` dans le dispatcher | `$1BEC` | `$104F0` |
| Table statique | `$1111E` | `$1FA22` |

La divergence documentaire `$12DF6` / `$12EF6` est résolue par leur rôle distinct : `$12DF6` est l’entrée appelée par la boucle de saisie; `$12EF6` est une cible interne du scanner qui lit la table statique `$1111E`. L’expérience a armé un breakpoint sur `$12DF6`; elle **n’a pas** observé de lecture à `$12EF6` sur une ligne rejetée. Le calcul absolu ne suppose pas qu’un offset TEXT soit une adresse : il ajoute la base d’image Hatari `$E904`.

## Procédure reproduite

Le profil D a été lancé par Hatari avec le fichier de commandes `work/p3c/fixtures/launch-d-natural.ini`; E avec `launch-e-natural.ini`. Les scripts de breakpoint en chaîne et la configuration restent sous `work/p3c/fixtures/`. Les options de lancement complètes sont dans la ligne de commande consignée dans les journaux de session et suivent le profil ci-dessus.

1. Démarrer l’interpréteur depuis le dossier `AUTO` d’un disque virtuel isolé.
2. Passer en mode direct avec `Shift-F9` (éditeur GFA), puis saisir `PRINT "A"` par événements clavier X11 et envoyer Return.
3. Breakpoint one-shot à TEXT `$12DF6`; sauvegarder la fenêtre mémoire pointée par A0 et les registres, puis armer `$1BD6`.
4. En D, lorsqu’un passage ultérieur a atteint `$1BD6`, enregistrer les registres et armer `$1BEC`. À `$1BEC`, résoudre A0 et arrêter l’exécution avant le corps cible.
5. Répéter la même séquence sous E avec la même ROM/configuration et un disque isolé.

La ligne n’a pas été chargée d’un fichier ni injectée dans la mémoire par le débogueur. Aucun fichier `.GFA`/`.BAS` exploitable n’a été trouvé dans les distributions locales examinées lors de P3-C; aucun fichier source natif n’a donc été créé ou sauvegardé. L’expérience est une saisie clavier normale, mais le texte attendu n’est pas celui finalement livré au parseur.

## Résultats

### Entrée parser et rejet

**OBSERVED — D.** Le breakpoint à `$216FA` s’est déclenché pendant la validation de la ligne saisie. À cet instant, les registres consignés dans la session Hatari sont `A0=$280F6`, `A1=$093A`, `A6=$27DA4`, `A7=$2E28E`; A0 pointe sur les octets ASCII `50 52 49 4E 54 20 33 41 33 0D`, soit `PRINT 3A3` suivi de CR. Un écran montre ensuite `Syntax Fehler`.

**OBSERVED — E.** Le breakpoint correspondant s’est déclenché à `$216FA`, avec `A0=$2804A`, `A1=$28054`, `A6=$27CF8`, `A7=$2E1F4`. La fenêtre sauvegardée autour de A0 contient également `PRINT 3A3` suivi de CR. L’écran montre `Syntax Error`.

La représentation `PRINT "A"` visée par la séquence X11 a été convertie en `PRINT 3A3`, vraisemblablement par le mapping AZERTY de la ROM invitée appliqué aux touches physiques émises par X11. Cette explication est **INFERRED** à partir de la ligne demandée et des octets capturés; le mapping exact de chaque touche n’a pas été cartographié. Les deux interpréteurs rejettent les mêmes octets, avec leurs libellés localisés. Ce rejet est une observation du chemin d’erreur, pas une validation de `PRINT`.

Les tables générées `$D2C` et `$10CC` n’ont pas été surveillées par watchpoints dans cette expérience. P3-B avait établi qu’elles sont des maps de rendu/texte et n’avait pas trouvé de flux démontré vers le dispatcher. Leur consultation lors de cette entrée est **UNMEASURED**. La lecture du texte statique `$1111E` à `$12EF6` est également **UNMEASURED** ici, car le breakpoint interne n’a pas été armé indépendamment.

### Dispatcher D

**OBSERVED, association ambiguë.** Dans le même processus D, le breakpoint `$104DA` a déclenché; à `$104F0`, Hatari a décodé `JSR (A0)` avec `A0=$14608`. Les registres au call étaient `A5=$282FA`, `D6=$0000024C`; à l’entrée du dispatcher, le dump consigné montre notamment `A5=$282F6`, `D6=$46`. Le décalage entre ces snapshots reflète les instructions exécutées entre l’entrée et l’appel.

La cible absolue `$14608` est résolue pour ce passage, mais le contrôle a été effectué après des saisies rejetées et la capture ne lie pas de manière univoque cette sélection à une instruction BASIC acceptée. Aucune sémantique n’est attribuée à cette cible. E n’a pas fourni de capture dispatcher comparable dans cette tentative. Le tableau de dispatch à 26 entrées de P3-B ne peut pas être directement invoqué pour expliquer ce passage sans établir l’état complet et la correspondance du vecteur.

### Comportement visible

**OBSERVED.** Les captures d’écran des deux runs affichent une erreur de syntaxe, française en D et anglaise en E. Aucun caractère `A` ni résultat numérique `3` n’apparaît comme résultat de `PRINT`. Le cas `PRINT 1+2` n’a pas été validé non plus : une tentative exploratoire a souffert du même problème de mapping et n’est pas retenue comme fixture.

## Équivalence E/D pour les observations retenues

| Observation | E | D | Classification / confiance |
|---|---|---|---|
| Hash PRG | `d44ca…b4c39` | `b7706…adf6e` | Binaires distincts; forte confiance (SHA-256) |
| Base TEXT dans Hatari | `$E904` | `$E904` | Identique dans ce profil; élevée |
| Entrée `$12DF6` exécutée | Absolue `$216FA` | Absolue `$216FA` | Les deux vues sont observées dans le debugger; élevée |
| Octets de ligne visés par l’essai | `PRINT 3A3 CR` | `PRINT 3A3 CR` | Identiques; haute sur les dumps disponibles |
| Réponse | `Syntax Error` | `Syntax Fehler` | Rejet observable; forte |
| Dispatcher / cible indirecte | Non mesurée | `$104DA` → `$104F0`, `A0=$14608` | Observation D isolée, association à la ligne ambiguë; faible pour tout lien sémantique |
| Accès aux maps `$D2C` / `$10CC` ou à `$1111E` | Non mesuré | Non mesuré | UNMEASURED |
| Résultat utilisateur attendu | Aucun | Aucun | Non démontré |

Ces observations concordent avec les différences de langue déjà établies par P1. Elles ne démontrent pas l’équivalence de traitement d’une instruction valide.

## Couverture et limites

* 2/2 exécutables et ROM vérifiés par SHA-256.
* 2/2 runs ont atteint le breakpoint d’entrée parser sur l’entrée clavier tentée.
* 2/2 ont capturé les mêmes octets de ligne et un rejet localisé.
* 1/2 a fourni une capture au point d’appel indirect du dispatcher; sa relation à la ligne est ambiguë.
* 0/2 instructions BASIC valides acceptées; 0/2 résultats attendus observés.
* 0 accès naturels aux deux maps générées et 0 lectures naturelles de `$1111E` confirmés.
* Aucun source natif/tokenisé sauvegardé; aucun test dynamique d’un fichier BASIC n’est revendiqué.

`rg-dis` 0.11.46 ne couvre qu’environ 25,3 % du TEXT des interpréteurs selon P3-B. L’expérience ne promeut aucune région `named.veto` en code. Les chemins directs d’erreur et les buffers non surveillés restent hors mesure. Les traces brutes et captures sont conservées dans `work/p3c/`; elles ne sont pas ajoutées à Git.

## Falsification et limites

L’essai visait à falsifier l’hypothèse qu’une saisie ordinaire `PRINT "A"` suffisait à traverser parser et dispatcher. Les dumps montrent au contraire que les octets réellement livrés diffèrent; la prémisse de l’expérience est donc falsifiée avant toute conclusion sur le handler. Répéter la même procédure sans déterminer le mapping du clavier ne constitue pas une validation.

La suite doit soit configurer une disposition clavier invitée connue, soit générer les bonnes touches ST à partir d’un mapping vérifié, soit sauvegarder une ligne par l’éditeur en prouvant les octets du fichier et son rechargement normal. Ensuite seulement, armer des watchpoints séparés sur `$1111E`, A6`+$D2C`, A6`+$10CC`, `$1BD6` et `$1BEC` dans des environnements E/D propres.

## Commandes et preuves

Hatari était lancé avec `--machine tt`, la ROM ci-dessus, `--harddrive work/p3c/drive-{d,e}`, `--cmd-fifo`, `--parse work/p3c/fixtures/launch-{d,e}-natural.ini`, `--trace os_base,gemdos`, et des fichiers de trace distincts. Les scripts de captures et la séquence d’entrées sont consignés sous `work/p3c/fixtures/`; les principaux éléments sont :

| Preuve brute | Contenu |
|---|---|
| `work/p3c/traces/d-natural-final.trace` | Événements OS/GEMDOS de démarrage D; SHA-256 `137419e08f8180577ba5c3caa0156938c6688e04cabda3ebe7df057366207288` |
| `work/p3c/traces/e-natural-final.trace` | Événements OS/GEMDOS de démarrage E; SHA-256 `7b70377f807f40dcc35a177530de6cdf7ca12a4bf537f29b7dd054342527e01f` |
| `work/p3c/traces/d-natural-parser-a0.bin` | A0 au parser D; SHA-256 `3546731983f23e4b87572c7feccc328587600b99712a9e97483363b7940c8c43` |
| `work/p3c/traces/e-natural-parser-window.bin` | fenêtre autour d’A0 au parser E; SHA-256 `5bb40fe9df00d11b5c29d2d1b6ed879ad3d0804b4d3cf90c6572c2eecd1903a3` |
| `work/p3c/traces/d-natural-dispatch-a5.bin` | espace A5 au dispatcher D; SHA-256 `1acef5de999ac6a37c3959583759799508526b41fbccf2c781fc356f93233a31` |
| `work/p3c/traces/d-natural-dispatch-frame.bin` | espace A5 au `JSR (A0)` D; SHA-256 `90dac4070c92371a3ec0fb41442555c3fd057af4e2f1acdd65dd0d1a7de60578` |
| `work/p3c/screenshots/d-natural-print-a-result.png` | rejet D; SHA-256 `4d96e2ed8fd6156f1bb934027f8d953aeacbcd9e1f353026947766d0a7f3667c` |
| `work/p3c/screenshots/e-natural-after-enter.png` | rejet E; SHA-256 `9e58e42f8e720ca47f9be73597683894c54631297875250fda0539aef9b231e5` |

## Questions ouvertes et transfert

1. Établir la traduction exacte X11 → scancode ST → caractère avec la ROM TOS française, ou neutraliser le mapping par une méthode normale de saisie.
2. Enregistrer une courte ligne valide depuis l’éditeur puis en vérifier le fichier, le hash et le rechargement naturel.
3. Refaire `PRINT "A"` puis `PRINT 1+2` sans breakpoints qui modifient l’état; capturer `$12DF6`, `$12EF6`, les lectures de `$1111E`, et les maps générées.
4. Répéter avec mêmes octets d’entrée E/D et suivre jusqu’au premier handler, puis seulement mesurer la sortie.

P3-C doit rester ouvert jusqu’à ce qu’une ligne valide soit acceptée et qu’une sélection de handler puisse lui être associée sans ambiguïté.
