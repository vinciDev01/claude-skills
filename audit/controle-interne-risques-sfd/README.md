# Guide d'utilisation : Skill `controle-interne-risques-sfd`

## 1. Ce que fait ce skill
Il conçoit et évalue le dispositif de contrôle interne d'un SFD selon l'Instruction BCEAO n° 017-12-2010 : cartographie des risques opérationnels, manuel de procédures, plan de contrôle permanent, rapport de contrôle global annuel, suivi des recommandations et calendrier réglementaire. C'est le pendant préventif de `auditeur-sfd-bceao`.

## 2. Contenu
* `references/instructions-bceao-017-018-2010.md` : synthèse des Instructions 017-12-2010 et 018-12-2010 (obligations, délais, contenu imposé des rapports), établie à partir du recueil officiel de la BCEAO.
* `references/bibliotheque-risques-sfd.csv` : 36 risques opérationnels types (caisse, épargne, crédit, tontine, trésorerie, comptabilité, informatique, LBC/FT, RH, gouvernance, continuité) avec contrôles clés et codes opération.
* `references/schemas-sfd.csv` : schémas d'écritures du core banking.
* `scripts/cartographie_risques.py` : calcule risques bruts et nets, classement, matrice et synthèse par processus.

## 3. Mots-clés déclencheurs
`contrôle interne`, `cartographie des risques`, `risque opérationnel`, `manuel de procédures`, `séparation des tâches`, `plan de contrôle`, `rapport de contrôle global`, `Instruction 017-12-2010`, `comité d'audit`, `suivi des recommandations`.

## 4. Exemples de questions
* « Établis la cartographie des risques opérationnels de notre COOPEC de 4 agences qui fait de la tontine. »
* « Rédige la procédure de caisse de fin de journée avec la séparation des tâches. »
* « Prépare la trame du rapport de contrôle global 2026 à transmettre à la BCEAO. »

```bash
python3 scripts/cartographie_risques.py references/bibliotheque-risques-sfd.csv --top 10
```
