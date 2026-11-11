# Guide d'utilisation : Skill `preparateur-balance`

## 1. Ce que fait ce skill
Il convertit une balance exportée d'Excel, d'un ERP ou d'un core banking au format `compte;libelle;debit;credit[;mouvement_debit]` utilisé par les autres skills (audit SFD, ratios BCEAO, analyse comptable). Il détecte l'en-tête et les colonnes, lit les montants au format français, retire titres et sous-totaux, rattache les comptes au plan SFD-BCEAO ou SYSCOHADA, puis contrôle l'équilibre.

## 2. Mots-clés déclencheurs
`balance`, `export`, `Excel`, `xlsx`, `CSV`, `Sage`, `core banking`, `importer`, `convertir`, `normaliser`, `format de balance`.

## 3. Exemples de questions
* « Voici l'export Excel de la balance de notre SFD au 30/09, prépare-la pour le calcul des ratios BCEAO. »
* « Ma balance Sage a des comptes à 8 chiffres et des totaux par classe, nettoie-la. »

## 4. Outil inclus

```bash
python3 scripts/normaliser_balance.py export.xlsx --apercu --plan sfd     # vérifier la détection
python3 scripts/normaliser_balance.py export.xlsx -o balance.csv --plan sfd
```

Le rapport de contrôle (JSON) liste les colonnes détectées, l'équilibre, les lignes écartées, les comptes rattachés au plan et les comptes hors plan.
