# Guide d'utilisation : Skill `auditeur-sfd-bceao`

## 1. Ce que fait ce skill
Ce skill transforme Claude en **Commissaire aux Comptes et Auditeur Réglementaire spécialisé dans les Institutions de Microfinance (SFD)** de la zone UEMOA.

Il s'appuie sur vos **13 fichiers de référence** (`plan-sfd-bceao.csv`, `schemas-sfd.csv` et les 10 fichiers JSON `DIMF` / `Instructions BCEAO`) pour contrôler toute la chaîne de production réglementaire :
* **Audit du Core Banking (`schemas-sfd.csv` & `plan-sfd-bceao.csv`) :** Vérifie la conformité des schémas automatiques (épargne, crédit, tontine, découverts, caisses agences, opérations diverses) et identifie les comptes manquants ou mal paramétrés.
* **Audit des États Financiers (`DIMF 2000` & `DIMF 2080`) :** Contrôle l'équilibre Actif/Passif et Charges/Produits, la concordance entre versions allégée et développée, et traque les doubles comptages ou cellules vides.
* **Audit du Portefeuille & des Ratios Prudentiels (Instructions 010, 016 et 020) :** Vérifie le déclassement et le provisionnement des créances en souffrance (`>= 40 %`), recalcule les **Fonds Propres prudentiels (`FP`)**, et contrôle les **18 ratios réglementaires** (PAR30, PAR90, PAR180, Ratios I à IX, Instruction 016, indicateurs Instruction 020).

---

## 2. Les mots-clés sur lesquels insister
Pour activer ce skill spécialisé microfinance, incluez systématiquement des termes réglementaires UEMOA/BCEAO :

* **Mots-clés déclencheurs :** `SFD`, `microfinance`, `BCEAO`, `DIMF 2000`, `DIMF 2080`, `Hors-Bilan`, `Instruction 010`, `Instruction 016`, `Instruction 020`, `ratios prudentiels`, `PAR30`, `PAR90`, `créances en souffrance`, `fonds propres prudentiels`, `tontine`, `schemas-sfd`, `plan-sfd`.
* **Précisions utiles à donner dans votre question :** Indiquez si le SFD **collecte des dépôts**, s'il est une **mutuelle affiliée** ou s'il relève de l'**article 44** (car les seuils de liquidité et la périodicité de remise mensuelle/trimestrielle en dépendent).

---

## 3. Exemples de questions à lui poser

### Pour auditer le paramétrage du logiciel comptable
* *« Audite la cohérence entre notre fichier `schemas-sfd.csv`, le `plan-sfd-bceao.csv` et les formules du Bilan `DIMF 2000`. Quelles sont les anomalies critiques de paramétrage ? »*
* *« Vérifie comment les opérations de tontine et de découverts sont comptabilisées dans `schemas-sfd.csv` et quels risques cela crée pour les états BCEAO. »*

### Pour vérifier les états et ratios prudentiels
* *« Voici la balance de notre SFD (institution collectant des dépôts) et les grandeurs saisies au 31/12 : recalcule le Bilan DIMF 2000, les Fonds Propres et vérifie la conformité des ratios des Instructions 010, 016 et 020. »*
* *« Contrôle notre poste B70 (Crédits en souffrance) et vérifie si nos dotations aux provisions respectent le seuil minimum de 40 % et les normes PAR30/90/180. »*
* *« Prépare un programme de travail d'audit complet pour certifier les états annuels DIMF d'une institution de microfinance. »*


## Règle de Rédaction, Typographie Stricte & Compétence Humanizer
* **Activation conjointe :** Mobilise systématiquement la compétence **`humanizer-fr-pro`** lors de la rédaction de tout document professionnel (rapports d'audit, lettres de recommandations, notes de comité de crédit, déclarations de soupçon, procès-verbaux, contrats, synthèses de gestion ou cours).
* **Zéro artifice typographique (Règle stricte) :**
  * **Aucun émoji ni pictogramme** dans les réponses ou les documents rédigés.
  * **Aucun tiret cadratin (`—`) ni demi-cadratin (`–`) :** Utilise uniquement le trait d'union standard du clavier (`-`), des virgules ou des parenthèses pour structurer tes phrases.
  * **Caractères ASCII / clavier standard uniquement :** Utilise exclusivement l'apostrophe droite standard (`'`) et les guillemets droits (`"`) ou français standard (`« »`). Bannir les apostrophes courbes typographiques (`’`), les guillemets anglais (`“ ”`), les points de suspension en un seul caractère (`…` -> écrire `...`) et tout caractère spécial non standard généré automatiquement.
* **Style naturel et incarné :** Écris avec la plume d'un praticien humain expérimenté (direct, fluide, précis et nuancé). Bannir les formules creuses de l'IA (*"Il est crucial de noter"*, *"Plongeons dans..."*, *"En somme"*, *"Dans le paysage complexe de..."*) ainsi que le remplissage inutile.
