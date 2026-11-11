# Guide d'utilisation : Skill `auditeur-compta-syscohada`

## 1. Ce que fait ce skill
Ce skill transforme Claude en **Auditeur Financier Senior / Commissaire aux Comptes** pour les entreprises commerciales et industrielles de l'espace OHADA.

Contrairement au comptable qui produit les comptes, l'auditeur adopte une posture de **scepticisme professionnel** basée sur les **normes d'audit internationales (ISA 315)** :
* **Contrôle par Assertions :** Vérifie l'Existence, l'Exhaustivité, l'Exactitude, la Séparation des exercices (Cut-off), les Droits & Obligations et la Présentation.
* **Chasse aux anomalies (*Red Flags*) :** Traque les caisses créditrices (`571`), les comptes d'attente non soldés (`471`), les écritures suspectes avant clôture, et les risques de redressement fiscal.
* **Livrables d'Audit :** Produit une **Feuille de Travail (Workpaper)** structurée par niveau de risque, propose les **écritures de redressement** (issues de `plan-comptable-syscohada-revise.csv`) et rédige des **recommandations de contrôle interne** (*Constat → Risque → Recommandation*).

---

## 2. Les mots-clés sur lesquels insister
Pour déclencher ce skill plutôt que celui du comptable, utilisez le vocabulaire de la révision et du contrôle :

* **Mots-clés déclencheurs :** `audite`, `révise`, `contrôle`, `anomalies`, `fraude`, `balance générale`, `grand livre`, `rapprochement bancaire`, `assertions`, `ISA`, `cut-off`, `contrôle interne`, `feuille de travail`, `redressement`, `circularisation`.
* **Pour le mode entraînement audit :** `entraîne-moi à l'audit`, `teste mes réflexes d'auditeur`, `cas pratique d'audit`.

---

## 3. Exemples de questions à lui poser

### Pour auditer des données réelles
* *« Voici notre balance générale avant inventaire : passe-la au crible, dresse une feuille de travail avec les anomalies détectées et propose les écritures de redressement. »*
* *« Audite le cycle Clients / Ventes de cette société : quels sont les risques sur l'assertion de séparation des exercices (cut-off) et quelles pièces dois-je demander ? »*
* *« Rédige une lettre de recommandations de contrôle interne (Management Letter) suite à la découverte d'un solde de caisse créditeur et de factures non normalisées. »*

### Pour s'entraîner aux réflexes d'auditeur
* *« Teste mes réflexes d'auditeur : donne-moi un extrait de balance piégé d'une PME OHADA et demande-moi mes 3 premiers contrôles avant de me révéler la solution. »*
