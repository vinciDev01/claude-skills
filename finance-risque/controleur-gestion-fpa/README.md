# Guide d'utilisation : Skill `controleur-gestion-fpa`

## 1. Ce que fait ce skill
Ce skill transforme Claude en **Contrôleur de Gestion Senior et Spécialiste FP&A (Financial Planning & Analysis)**. 

Tandis que les autres skills vérifient le passé (comptabilité, audit, fiscalité), celui-ci vous aide à **piloter la rentabilité future et prendre des décisions business** pour une PME (SYSCOHADA) ou une Institution de Microfinance / SFD (BCEAO) :
* **Budgets & Trésorerie :** Construit des budgets prévisionnels, des plans de trésorerie glissants (cash-flow) et des simulations *What-If* (scénarios pessimiste, central, optimiste).
* **Coûts & Seuil de Rentabilité :** Sépare les charges fixes et variables, calcule la marge sur coût variable (MCV), le point mort (en FCFA et en volume/nombre de crédits) et le coût de revient.
* **Pilotage SFD / Agences :** Analyse la rentabilité par agence ou par produit (crédit classique, tontine, épargne), suit la productivité des agents de crédit et le coefficient d'exploitation.
* **Analyse des Écarts :** Explique les écarts entre le Réel et le Budget en distinguant l'effet volume de l'effet prix/taux.

---

## 2. Les mots-clés sur lesquels insister
Pour déclencher ce skill et obtenir une modélisation orientée décision, utilisez ces mots-clés :

* **Mots-clés déclencheurs :** `budget`, `prévisionnel`, `trésorerie glissante`, `cash-flow`, `seuil de rentabilité`, `point mort`, `coût de revient`, `charges fixes`, `charges variables`, `marge sur coût variable`, `analyse des écarts`, `réel vs budget`, `rentabilité par agence`, `rentabilité par produit`, `tableau de bord`, `KPI`, `scénario`, `simulation`.
* **Précisions utiles :** Donnez vos hypothèses clés (volume d'activité, taux d'intérêt moyen, délais de paiement clients/fournisseurs, charges fixes mensuelles) pour que Claude construise un modèle sur mesure.

---

## 3. Exemples de questions à lui poser

### Pour une PME / Entreprise (SYSCOHADA)
* *« Voici nos charges et produits de l'année : sépare les charges fixes et variables, calcule notre seuil de rentabilité (point mort) et dis-moi quel chiffre d'affaires minimum nous devons réaliser chaque mois pour être rentables. »*
* *« Construis un plan de trésorerie prévisionnel sur 6 mois en tenant compte d'un délai client de 45 jours, d'un paiement fournisseurs à 30 jours et de nos échéances fiscales OTR/CNSS. »*
* *« Analyse l'écart entre notre budget et notre réalisé du trimestre et décompose-le entre effet volume et effet prix. »*

### Pour une Institution de Microfinance / SFD
* *« Évalue la rentabilité de nos 3 agences (Lomé Centre, Kara, Sokodé) en répartissant les frais du siège, et propose un plan d'action pour redresser l'agence déficitaire. »*
* *« Simule l'impact sur notre coefficient d'exploitation et notre résultat net si nous recrutons 5 nouveaux agents de crédit avec un objectif de 140 emprunteurs actifs chacun. »*

---

## 4. Outil de calcul inclus

`scripts/seuil_rentabilite.py` calcule la MCV, le seuil de rentabilité en valeur et en volume, la marge et l'indice de sécurité, le levier opérationnel et la date du point mort (activité régulière ou CA mensuel saisonnier).

```bash
python3 scripts/seuil_rentabilite.py --ca 120000000 --cv 78000000 --cf 30000000 --debut-exercice 2026-01-01
```
