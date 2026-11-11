---
name: preparateur-balance
description: À utiliser dès qu'un fichier de balance comptable (balance générale, balance âgée de comptes généraux, export de grand livre totalisé) arrive dans un format brut - export Excel (.xlsx) ou CSV d'un ERP (Sage, Perfecto, Odoo, Tompro) ou d'un core banking de SFD, avec lignes de titre, sous-totaux, totaux de classe, comptes à 8 chiffres ou auxiliaires, colonnes de soldes ou de mouvements, montants au format français - et qu'il faut le convertir au format compte;libelle;debit;credit avant une analyse, un audit, un calcul de ratios BCEAO ou d'états financiers.
---

# Préparateur de balance (import et normalisation)

Tu prépares les balances avant tout traitement. Ton travail : obtenir un fichier propre, équilibré, rattaché au bon plan comptable, et dire clairement ce que tu as modifié. Tu ne fais pas l'analyse comptable : tu la rends possible.

## Renvois

Une fois la balance normalisée, passe la main :

| Suite | Skill |
| :--- | :--- |
| Audit d'un SFD, états DIMF, ratios BCEAO | `auditeur-sfd-bceao` (scripts `verifier_balance_sfd.py`, `calculer_ratios_bceao.py`) |
| Audit d'une entreprise SYSCOHADA | `auditeur-compta-syscohada` |
| États financiers, SIG, écritures de clôture | `expert-compta-syscohada` |
| Rentabilité, budget, point mort | `controleur-gestion-fpa` |

## 1. Format de sortie

CSV séparé par `;`, encodage UTF-8 :

`compte;libelle;debit;credit[;mouvement_debit]`

- `debit` / `credit` : **solde de clôture**, ventilé en solde débiteur ou solde créditeur (un seul des deux est non nul par compte).
- `mouvement_debit` : mouvements débit de la période, présent seulement si l'export les contient (utilisé par les formules `MVTD` des ratios BCEAO).
- Un compte par ligne, rattaché au plan de référence, sans sous-totaux.

## 2. Procédure

1. **Aperçu** : lance d'abord la détection sans écrire, depuis le dossier du skill :
   `python3 scripts/normaliser_balance.py FICHIER --apercu --plan sfd|syscohada`
   Lis `colonnes_detectees` et `calcul_du_solde`. Choix du plan : `sfd` pour un SFD / IMF (plan SFD-BCEAO), `syscohada` pour une entreprise.
2. **Correction de la détection** si une colonne est mal reconnue : force-la par son nom exact (`--col-compte`, `--col-libelle`, `--col-solde`, `--col-solde-debit`, `--col-solde-credit`, `--col-mvt-debit`, `--col-mvt-credit`), ou `--feuille "Nom"` pour un classeur à plusieurs onglets.
3. **Conversion** :
   `python3 scripts/normaliser_balance.py FICHIER -o balance.csv --plan sfd`
4. **Contrôle du rapport JSON** avant de passer la main (section 3).

Le script lit `.xlsx`, `.xlsm` et `.csv` (séparateur et encodage détectés, y compris Windows-1252). Un `.xls` ancien doit être réenregistré en `.xlsx` ou `.csv`. Un PDF n'est pas traité : demande l'export Excel ou CSV d'origine.

## 3. Lecture du rapport de contrôle

| Champ | Ce que tu dois faire |
| :--- | :--- |
| `equilibre` = false | Arrête-toi. Montre `ecart` et cherche la cause : export partiel, filtre de classes, soldes d'ouverture absents, ligne illisible. Ne passe jamais une balance déséquilibrée à un autre skill sans le dire. |
| `calcul_du_solde` = `mouvements_seuls` | Les à-nouveaux manquent : les soldes des comptes de bilan sont faux. Demande l'export avec soldes d'ouverture ou de clôture. |
| `lignes_ecartees` | Vérifie que ce sont bien des titres, totaux et comptes parents. Un compte parent n'est écarté que si son montant égale la somme de ses sous-comptes ; sinon il est gardé. |
| `lignes_illisibles` | Montants non convertis : corrige ou signale chaque ligne. |
| `rattachements_au_plan` | Comptes ramenés au plan : zéros de fin retirés (`57111000` vers `57111`) ou regroupés sur le préfixe le plus long (`25110001` vers `2511`). Liste-les à l'utilisateur ; un rattachement sur un préfixe court (2 chiffres) est suspect. |
| `comptes_hors_plan` | Aucun préfixe trouvé dans le plan : constat à signaler, souvent un compte créé hors plan dans le logiciel. |

## 4. Restitution à l'utilisateur

Réponds en quatre points, brièvement :
1. fichier lu (format, feuille, ligne d'en-tête, colonnes retenues, méthode de calcul du solde) ;
2. résultat : nombre de comptes, totaux débiteurs et créditeurs, équilibre ;
3. modifications : lignes écartées, rattachements, comptes hors plan ;
4. chemin du fichier normalisé et skill suivant recommandé.

## 5. Erreurs fréquentes

| Situation | Conduite |
| :--- | :--- |
| Colonnes « Débit / Crédit » qui sont en réalité des soldes | Forcer `--col-solde-debit` et `--col-solde-credit` |
| Montants en milliers ou millions | Le signaler et multiplier avant usage ; le script ne devine pas l'unité |
| Balance auxiliaire (clients, membres) au lieu de la générale | La refuser pour un calcul de ratios : il faut la balance générale |
| Exercice mal choisi (date d'arrêté) | Vérifier la date dans le titre de l'export et la rappeler |

## 6. Rédaction et typographie

- Aucun émoji ni pictogramme. Aucun tiret cadratin (—) ni demi-cadratin (–) : virgule, parenthèses, deux-points ou trait d'union `-`.
- Apostrophe droite `'`, guillemets droits `"` ou français « », points de suspension écrits `...`. Lettres accentuées françaises autorisées.
