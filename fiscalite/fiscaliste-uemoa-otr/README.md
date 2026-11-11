# Guide d'utilisation : Skill `fiscaliste-uemoa-otr`

## 1. Ce que fait ce skill
Ce skill transforme Claude en **Conseil Fiscal Agréé et Expert en Déclarations Sociales** spécialisé dans la zone **UEMOA**, avec un ancrage complet sur le **Togo (Office Togolais des Recettes - OTR, CNSS et AMU)**.

Il vous accompagne sur 4 grands axes :
* **Détermination du Résultat Fiscal & Liasse :** Calcule le passage du résultat comptable au résultat fiscal (réintégrations des charges non déductibles, déductions, arbitrage IS vs IMF).
* **Gestion de la TVA & TAF :** Vérifie l'assujettissement, le droit à déduction, les exclusions légales, l'exigence de facture normalisée OTR et le calcul du prorata de TVA (indispensable pour les SFD/microfinances).
* **Retenues à la Source (RAS) :** Calcule les retenues sur prestations de services (avec ou sans Attestation de Régularité Fiscale), les retenues sur prestataires non-résidents (20 % / conventions UEMOA), la retenue sur loyer (RSL) et l'IRCM.
* **Paie & Charges Sociales :** Établit des bulletins de paie complets (CNSS 17,5 % patronal / 4 % salarial, AMU, IRPP sur salaires), calcule le coût total employeur et génère les écritures de paie.

---

## 2. Les mots-clés sur lesquels insister
Pour déclencher ce skill et obtenir une réponse précise et chiffrée, utilisez les mots-clés suivants :

* **Mots-clés déclencheurs :** `OTR`, `CGI`, `fiscalité`, `résultat fiscal`, `réintégration`, `déductible`, `IS`, `IMF`, `TVA`, `TAF`, `prorata`, `facture normalisée`, `retenue à la source`, `attestation de régularité fiscale`, `RSL`, `loyer`, `IRCM`, `CNSS`, `AMU`, `IRPP`, `bulletin de paie`, `liasse fiscale`.
* **Précisions utiles :** Indiquez toujours le **pays** (par défaut le Togo), le **régime d'imposition** (Réel ou TPU), et si le prestataire dispose d'une **Attestation de Régularité Fiscale (ARF)** en cours de validité.

---

## 3. Exemples de questions à lui poser

### Fiscalité des entreprises et SFD
* *« Voici notre résultat comptable avant impôt et une liste de charges sensibles (amendes OTR, cadeaux clients, frais de réception, provisions). Calcule les réintégrations extracomptables, le résultat fiscal et compare l'IS à l'IMF. »*
* *« Nous avons payé un consultant informatique résident au Togo qui n'a pas d'Attestation de Régularité Fiscale, ainsi qu'un cabinet basé à Abidjan (UEMOA). Quelles retenues à la source devons-nous opérer et quelles sont les écritures comptables ? »*
* *« En tant que SFD (institution de microfinance) au Togo, comment devons-nous gérer la TVA sur nos achats informatiques et nos frais généraux alors que nos intérêts de crédit sont exonérés ? »*

### Paie et déclarations sociales
* *« Calcule le bulletin de paie complet et le coût total employeur pour un cadre au Togo perçevant un salaire brut de 450 000 FCFA (CNSS, AMU, IRPP) et passe l'écriture comptable correspondante. »*
* *« Quelles sont toutes nos obligations déclaratives et dates limites auprès de l'OTR et de la CNSS pour le mois qui s'achève ? »*

---

## Outil de calcul inclus

`scripts/calcul_paie_togo.py` calcule un bulletin de paie togolais complet : CNSS (4 % / 17,5 %), AMU (5 % / 5 %), IRPP (abattement de 28 %, charges de famille, barème de l'art. 74 CGI), net à payer, coût employeur, montants à reverser et écritures comptables.

```bash
python3 scripts/calcul_paie_togo.py 450000 --charges 3
```

Les taux et le barème sont dans `references/parametres-paie-togo.json`, avec leurs sources et la date de vérification. À mettre à jour à chaque loi de finances ou décret CNSS / AMU. Le script reproduit au franc près les exemples publiés par les guides IRPP 2026.
