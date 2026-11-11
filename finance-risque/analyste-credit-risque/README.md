# Guide d'utilisation : Skill `analyste-credit-risque`

## 1. Ce que fait ce skill
Ce skill transforme Claude en **Analyste Crédit Senior et Directeur des Risques**, agissant comme un véritable **Comité de Crédit** pour les Institutions de Microfinance (SFD), banques et entreprises de la zone **OHADA / UEMOA**.

Il couvre tout le cycle de vie d'un crédit :
* **Instruction & Scoring (Les 5 "C") :** Évalue la moralité/historique, reconstruit la capacité de remboursement réelle (`DSCR >= 1,25x` pour les pros, taux d'endettement `<= 33-40 %` pour les particuliers), vérifie l'apport personnel et analyse les risques sectoriels.
* **Calculs Financiers & Conformité :** Calcule les échéanciers, le **Taux Effectif Global (TEG)**, et vérifie le respect des plafonds prudentiels BCEAO (**Ratio III** prêts aux dirigeants/personnel et **Ratio IV** division des risques `<= 10 %` des Fonds Propres).
* **Sûretés OHADA :** Évalue la valeur de réalisation (avec décote) des garanties (épargne bloquée `2545`, cautionnement solidaire, gage, hypothèque, nantissement).
* **Recouvrement & Restructuration :** Définit des plans d'action gradués (amiable, pré-contentieux, contentieux) et encadre les rééchelonnements sans fausser les indicateurs `PAR30`/`PAR90`.

---

## 2. Les mots-clés sur lesquels insister
Pour activer ce skill et obtenir une note de comité de crédit complète, utilisez ces mots-clés :

* **Mots-clés déclencheurs :** `dossier de crédit`, `octroi`, `scoring`, `capacité de remboursement`, `DSCR`, `taux d'endettement`, `comité de crédit`, `garantie`, `sûreté OHADA`, `caution`, `épargne nantie`, `échéancier`, `TEG`, `impayé`, `recouvrement`, `restructuration`, `rééchelonnement`, `PAR30`, `division des risques`.
* **Informations utiles à fournir :** Montant demandé, objet du crédit, durée souhaitée, taux d'intérêt, revenus ou chiffre d'affaires/charges du client, encours de dettes existantes et garanties proposées.

---

## 3. Exemples de questions à lui poser

### Instruction d'un dossier de crédit
* *« Instruis ce dossier de crédit PME : demande de 15 000 000 FCFA sur 24 mois à 14 % l'an pour financer un stock de marchandises. Voici son chiffre d'affaires mensuel, ses charges et ses garanties. Donne-moi le calcul du DSCR, le scoring et ton avis de Comité de Crédit. »*
* *« Un employé du SFD sollicite un prêt immobilier. Nos Fonds Propres sont de 120 000 000 FCFA et l'encours actuel des prêts au personnel/dirigeants est de 10 500 000 FCFA. Quel montant maximum pouvons-nous lui accorder sans violer le Ratio III de la BCEAO ? »*

### Gestion des impayés et recouvrement
* *« Un client commerçant ayant un crédit de 5 000 000 FCFA accuse 45 jours de retard suite à un sinistre sur son marché. Propose une stratégie de recouvrement et analyse l'opportunité d'un rééchelonnement sans masquer le risque PAR. »*

---

## 4. Outil de calcul inclus

`scripts/tableau_amortissement.py` produit l'échéancier (annuités constantes ou amortissement constant, avec différé partiel), le coût total du crédit, le TEG proportionnel et actuariel (frais de dossier et assurance inclus) et le DSCR.

```bash
python3 scripts/tableau_amortissement.py 15000000 14 24 --frais-dossier 150000 --cash-flow 1100000
```
