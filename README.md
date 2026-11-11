# Skills Comptabilité, Audit, Finance et Droit (OHADA / UEMOA)

Ce répertoire regroupe **douze skills** qui font de Claude une équipe d'experts comptables, auditeurs, fiscalistes, analystes et juristes pour l'espace **OHADA** et l'**UEMOA (BCEAO)**. Les skills sont rangés par domaine. Chaque dossier de skill est autonome : il contient son `SKILL.md`, ses fichiers `references/` et, le cas échéant, ses `scripts/`.

## Organisation

```
comptabilite/            expert-compta-syscohada, mentor-compta-anglosaxon (+ .zip), preparateur-balance
audit/                   auditeur-compta-syscohada, auditeur-sfd-bceao, controle-interne-risques-sfd
fiscalite/               fiscaliste-uemoa-otr
finance-risque/          controleur-gestion-fpa, analyste-credit-risque
juridique-conformite/    juriste-ohada-gouvernance, conformite-lbc-ft-bceao
redaction/               humanizer-fr-pro
```

Pour installer ou zipper un skill, prendre son dossier (ex. `audit/auditeur-sfd-bceao/`), pas le dossier de domaine. Les commandes `python3 scripts/...` ci-dessous s'exécutent depuis le dossier du skill.

---

## Vue d'ensemble

| N° | Skill (= dossier) | Domaine | Rôle | Référentiel | Scripts |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `expert-compta-syscohada` | comptabilite | Production comptable, clôture, états financiers, SIG, conseil au dirigeant | SYSCOHADA révisé (AUDCIF) | |
| 2 | `mentor-compta-anglosaxon` | comptabilite | Apprentissage progressif (niveaux 1 à 4), comptes en T, méthode socratique | Pédagogie CPA/ACCA et SYSCOHADA révisé | |
| 3 | `auditeur-compta-syscohada` | audit | Révision des comptes d'entreprise, contrôle interne, anomalies, feuille de travail | SYSCOHADA révisé et normes ISA | |
| 4 | `auditeur-sfd-bceao` | audit | Audit des SFD : schémas CBS, états DIMF, fonds propres, ratios prudentiels | RCSFD, Instructions BCEAO 010, 016, 020 | contrôle de balance, calcul des ratios |
| 5 | `fiscaliste-uemoa-otr` | fiscalite | Résultat fiscal, TVA/TAF, retenues à la source, paie, CNSS/AMU | CGI Togo (OTR), UEMOA | bulletin de paie Togo |
| 6 | `controleur-gestion-fpa` | finance-risque | Budgets, trésorerie, coûts, point mort, rentabilité agences et produits | Comptabilité analytique, KPIs SFD | seuil de rentabilité |
| 7 | `analyste-credit-risque` | finance-risque | Instruction de crédit, scoring, TEG/DSCR, sûretés, recouvrement | Comité de crédit, AUS, ratios BCEAO | échéancier et TEG |
| 8 | `conformite-lbc-ft-bceao` | juridique-conformite | KYC, PPE, opérations atypiques, déclaration de soupçon | Loi uniforme LBC/FT, BCEAO, CENTIF | |
| 9 | `juriste-ohada-gouvernance` | juridique-conformite | AG/CA, PV, affectation du résultat, conventions, contrats | Actes uniformes OHADA, loi SFD | |
| 10 | `humanizer-fr-pro` | redaction | Relecture et réécriture des livrables pour supprimer le ton « IA » | Règles de style et de typographie | |
| 11 | `preparateur-balance` | comptabilite | Conversion des balances Excel / ERP / core banking au format des skills, contrôle d'équilibre | Plans SFD-BCEAO et SYSCOHADA | normalisation de balance |
| 12 | `controle-interne-risques-sfd` | audit | Cartographie des risques opérationnels, procédures, plan de contrôle, rapport de contrôle global | Instructions BCEAO 017-12-2010 et 018-12-2010 | cartographie des risques |

## Quel skill pour quelle demande ?

Les skills se renvoient les uns aux autres. Les frontières principales :

- **Passer une écriture** pour une entreprise : `expert-compta-syscohada`. **Apprendre** ou s'entraîner : `mentor-compta-anglosaxon`.
- **Auditer** une entreprise commerciale : `auditeur-compta-syscohada`. Auditer un **SFD / IMF** : `auditeur-sfd-bceao`.
- **Un dossier de crédit** précis : `analyste-credit-risque`. **Le portefeuille** ou les ratios dans leur ensemble : `auditeur-sfd-bceao`.
- **Un flux suspect** : `conformite-lbc-ft-bceao` d'abord, le recouvrement ensuite.
- **Une balance en Excel ou export d'ERP** : `preparateur-balance` d'abord, puis le skill d'analyse.
- **Constater** des anomalies dans un SFD : `auditeur-sfd-bceao`. **Organiser** le dispositif qui les prévient : `controle-interne-risques-sfd`.

---

## 1. `comptabilite/expert-compta-syscohada`
Passe les écritures courantes et complexes avec les seuls comptes de `plan-comptable-syscohada-revise.csv`, vérifie l'équilibre, liste les pièces justificatives et chiffre l'impact sur VA, EBE, CAFG, BFE et trésorerie. Pas de cours : les demandes d'apprentissage vont au mentor.

* « Comptabilise cette facture d'acquisition d'immobilisation avec frais accessoires et TVA selon le SYSCOHADA révisé. »

## 2. `comptabilite/mentor-compta-anglosaxon`
Enseigne des flux économiques jusqu'aux écritures complexes, en partant de l'équation `Actif = Dettes + Capitaux propres`, avec comptes en T, questions socratiques et un défi « Et si... » à la fin de chaque correction.

* « Démarre le cours au niveau 1 sur l'équation comptable et pose-moi un cas pratique. »

## 3. `audit/auditeur-compta-syscohada`
Scepticisme professionnel, assertions ISA 315, seuil de signification, signaux d'alerte (caisse créditrice, comptes d'attente, habillage de bilan), feuille de travail, écritures de redressement et lettre de recommandations. Inclut un mode entraînement.

* « Voici la balance avant inventaire : identifie les anomalies et propose les écritures de redressement. »

## 4. `audit/auditeur-sfd-bceao`
Audit du paramétrage (`schemas-sfd.csv`, `plan-sfd-bceao.csv`), des états DIMF 2000 / 2080 / hors-bilan, des fonds propres et des ratios des Instructions 010, 016 et 020. Deux scripts :

```bash
python3 scripts/verifier_balance_sfd.py balance.csv
python3 scripts/calculer_ratios_bceao.py balance.csv valeurs.json [--n1 balance_n1.csv]
```

La balance est un CSV `compte;libelle;debit;credit`. `valeurs.json` contient le statut du SFD et les grandeurs extra-comptables (codes listés dans `references/grandeurs.json`) ; sans lui, les ratios qui en dépendent ne sont pas calculables.

## 5. `fiscalite/fiscaliste-uemoa-otr`
Passage au résultat fiscal, IS contre IMF, TVA et prorata, TAF, retenues à la source, IRCM, paie, CNSS et AMU, échéances et sanctions. Les taux fiscaux non vérifiés sont rassemblés dans un tableau de **paramètres à confirmer** ; les paramètres de paie, eux, ont été vérifiés sur les sources officielles.

* « Voici notre résultat comptable et nos charges sensibles : calcule les réintégrations, le résultat fiscal et compare l'IS à l'IMF. »

```bash
python3 scripts/calcul_paie_togo.py 450000 --charges 3
```

Les paramètres de paie (CNSS, AMU, barème IRPP) sont sourcés et datés dans `references/parametres-paie-togo.json`.

## 6. `finance-risque/controleur-gestion-fpa`
Budgets, plan de trésorerie, scénarios, coûts (complets, direct costing, ABC), point mort, écarts volume / prix, rentabilité par agence et par produit pour les SFD.

```bash
python3 scripts/seuil_rentabilite.py --ca 120000000 --cv 78000000 --cf 30000000 --debut-exercice 2026-01-01
```

## 7. `finance-risque/analyste-credit-risque`
Les 5 C du crédit, plafonds Ratio III et IV, sûretés OHADA avec décote, recouvrement gradué, note de comité avec avis motivé.

```bash
python3 scripts/tableau_amortissement.py 15000000 14 24 --frais-dossier 150000 --cash-flow 1100000
```

## 8. `juridique-conformite/conformite-lbc-ft-bceao`
Vigilance clientèle et bénéficiaires effectifs, PPE, listes de sanctions, signaux d'alerte propres aux SFD (fractionnement, tontine, remboursement anticipé en espèces), projet de déclaration de soupçon factuel, rappel de l'interdiction d'alerter le client.

* « Un client déclarant 300 000 FCFA de revenus mensuels a fait 6 dépôts de 1 900 000 FCFA en 10 jours puis soldé son crédit. Analyse et rédige un projet de DOS. »

## 9. `juridique-conformite/juriste-ohada-gouvernance`
Vie sociale (AGO dans les 6 mois, réserve légale, capitaux propres inférieurs à la moitié du capital), conventions réglementées et interdites, gouvernance SFD, rédaction de PV, contrats et mises en demeure avec champs `[À compléter]`.

* « Rédige le PV de l'AGO d'approbation des comptes 2025 de notre SA avec affectation du résultat. »

## 10. `redaction/humanizer-fr-pro`
Supprime les tics d'écriture IA d'un texte français sans en changer le fond. Les autres skills l'appellent pour finaliser leurs livrables quand il est installé.

---

## 11. `comptabilite/preparateur-balance`
Détecte l'en-tête et les colonnes d'un export (xlsx ou csv, encodage Windows inclus), lit les montants au format français, retire titres, totaux et comptes parents, rattache les comptes au plan (`57111000` vers `57111`), contrôle l'équilibre et produit le CSV attendu par les autres skills, avec un rapport de ce qui a été modifié.

```bash
python3 scripts/normaliser_balance.py export.xlsx --apercu --plan sfd
python3 scripts/normaliser_balance.py export.xlsx -o balance.csv --plan sfd
```

## 12. `audit/controle-interne-risques-sfd`
Conçoit le dispositif de contrôle interne exigé par l'Instruction BCEAO 017-12-2010 : cartographie des risques à partir d'une bibliothèque de 36 risques types reliés aux codes opération du core banking, manuel de procédures avec séparation des tâches, plan de contrôle permanent, rapport de contrôle global (11 rubriques imposées, 6 mois après la fin de l'année), suivi des recommandations et calendrier réglementaire.

```bash
python3 scripts/cartographie_risques.py references/bibliotheque-risques-sfd.csv --top 10
```

---

## Règles de rédaction communes

Chaque skill porte ses propres règles, pour fonctionner même sans `humanizer-fr-pro` :

* aucun émoji ni pictogramme ;
* aucun tiret cadratin ni demi-cadratin : virgule, parenthèses, deux-points ou trait d'union `-` ;
* apostrophe droite `'`, guillemets droits `"` ou français « », points de suspension écrits `...` ; lettres accentuées autorisées, pas d'autres caractères spéciaux susceptibles de corrompre un ERP ou un document juridique ;
* ton direct d'un praticien senior, sans formules creuses.

## Maintenance

Les fichiers de référence sont dupliqués volontairement dans chaque skill qui en a besoin, pour que chaque dossier reste autonome une fois installé ou zippé. Après une mise à jour d'un fichier de référence, recopier la nouvelle version dans tous les dossiers concernés (`md5sum */*/references/*` permet de vérifier qu'ils sont identiques).
