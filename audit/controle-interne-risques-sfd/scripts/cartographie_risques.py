#!/usr/bin/env python3
"""Cartographie des risques opérationnels : risque brut, risque net, priorités, matrice.

Entrée : CSV séparé par ';' avec au minimum les colonnes
  risque;probabilite;impact
et en option : code;processus;maitrise;controles_cles;... (colonnes conservées).
Le modèle references/bibliotheque-risques-sfd.csv peut servir de point de départ.

Échelles (1 à 4) :
  probabilite : 1 rare, 2 possible, 3 probable, 4 quasi certain (sur 12 mois)
  impact      : 1 faible, 2 modéré, 3 grave, 4 critique (financier, réglementaire, réputation)
  maitrise    : 1 inexistante, 2 insuffisante, 3 acceptable, 4 forte (dispositif de contrôle actuel)

Risque brut = probabilite x impact (1 à 16).
Risque net  = brut x coefficient de maîtrise (1 : 1,00 ; 2 : 0,75 ; 3 : 0,50 ; 4 : 0,25).
Criticité   : >= 12 critique, 8 à 11,99 élevé, 4 à 7,99 modéré, < 4 faible.

Exemples :
  python3 cartographie_risques.py references/bibliotheque-risques-sfd.csv
  python3 cartographie_risques.py ma_carto.csv --processus Crédit --top 10
  python3 cartographie_risques.py ma_carto.csv --sortie carto_calculee.csv --json
"""
import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

COEF_MAITRISE = {1: 1.0, 2: 0.75, 3: 0.5, 4: 0.25}
LIB = {"probabilite": "Probabilité", "impact": "Impact", "maitrise": "Maîtrise"}


def criticite(score):
    if score >= 12:
        return "Critique"
    if score >= 8:
        return "Élevé"
    if score >= 4:
        return "Modéré"
    return "Faible"


def entier(val, nom, ligne, defaut=None):
    try:
        v = int(str(val).strip())
    except (TypeError, ValueError):
        if defaut is not None and (val is None or str(val).strip() == ""):
            return defaut
        sys.exit(f"Ligne {ligne} : {LIB[nom]} illisible ({val!r}), attendu un entier de 1 à 4.")
    if not 1 <= v <= 4:
        sys.exit(f"Ligne {ligne} : {LIB[nom]} = {v}, hors de l'échelle 1 à 4.")
    return v


def main():
    ap = argparse.ArgumentParser(description="Cartographie des risques opérationnels")
    ap.add_argument("fichier", type=Path)
    ap.add_argument("--processus", help="filtrer sur un processus")
    ap.add_argument("--top", type=int, default=0, help="n'afficher que les N risques nets les plus élevés")
    ap.add_argument("--sortie", type=Path, help="CSV enrichi des scores à écrire")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    with open(a.fichier, encoding="utf-8-sig") as f:
        lignes = list(csv.DictReader(f, delimiter=";"))
    if not lignes or not {"risque", "probabilite", "impact"} <= set(lignes[0]):
        sys.exit("Colonnes obligatoires : risque;probabilite;impact (séparateur ';').")

    risques = []
    for n, r in enumerate(lignes, start=2):
        if a.processus and r.get("processus", "").lower() != a.processus.lower():
            continue
        p = entier(r["probabilite"], "probabilite", n)
        i = entier(r["impact"], "impact", n)
        m = entier(r.get("maitrise"), "maitrise", n, defaut=1)
        brut = p * i
        net = round(brut * COEF_MAITRISE[m], 2)
        risques.append({**r, "probabilite": p, "impact": i, "maitrise": m, "risque_brut": brut,
                        "criticite_brute": criticite(brut), "risque_net": net, "criticite_nette": criticite(net)})

    risques.sort(key=lambda r: (-r["risque_net"], -r["risque_brut"]))
    affiches = risques[: a.top] if a.top else risques

    matrice = Counter((r["probabilite"], r["impact"]) for r in risques)
    synthese = {
        "nombre_risques": len(risques),
        "criticite_nette": dict(Counter(r["criticite_nette"] for r in risques)),
        "criticite_brute": dict(Counter(r["criticite_brute"] for r in risques)),
        "par_processus": {},
    }
    for r in risques:
        proc = r.get("processus") or "(non précisé)"
        s = synthese["par_processus"].setdefault(proc, {"risques": 0, "net_moyen": 0.0, "net_max": 0.0})
        s["risques"] += 1
        s["net_moyen"] += r["risque_net"]
        s["net_max"] = max(s["net_max"], r["risque_net"])
    for s in synthese["par_processus"].values():
        s["net_moyen"] = round(s["net_moyen"] / s["risques"], 2)

    if a.sortie:
        champs = list(risques[0].keys()) if risques else []
        with open(a.sortie, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=champs, delimiter=";")
            w.writeheader()
            w.writerows(risques)

    if a.json:
        print(json.dumps({"synthese": synthese, "risques": affiches,
                          "matrice_probabilite_impact": {f"P{p}xI{i}": n for (p, i), n in sorted(matrice.items())}},
                         ensure_ascii=False, indent=2))
        return

    print(f"{len(risques)} risques évalués. Criticité nette : "
          + ", ".join(f"{k} {v}" for k, v in sorted(synthese['criticite_nette'].items())))
    print()
    print("| Rang | Code | Processus | Risque | Brut | Maîtrise | Net | Criticité nette |")
    print("| ---: | :--- | :--- | :--- | ---: | ---: | ---: | :--- |")
    for k, r in enumerate(affiches, 1):
        print(f"| {k} | {r.get('code', '')} | {r.get('processus', '')} | {r['risque']} | {r['risque_brut']} | "
              f"{r['maitrise']} | {r['risque_net']:g} | {r['criticite_nette']} |")
    print()
    print("Matrice des risques bruts (nombre de risques ; lignes = impact, colonnes = probabilité)")
    print("| Impact \\ Probabilité | 1 | 2 | 3 | 4 |")
    print("| :--- | ---: | ---: | ---: | ---: |")
    for i in (4, 3, 2, 1):
        print(f"| {i} | " + " | ".join(str(matrice.get((p, i), 0)) for p in (1, 2, 3, 4)) + " |")
    print()
    print("| Processus | Risques | Net moyen | Net max |")
    print("| :--- | ---: | ---: | ---: |")
    for proc, s in sorted(synthese["par_processus"].items(), key=lambda x: -x[1]["net_max"]):
        print(f"| {proc} | {s['risques']} | {s['net_moyen']:g} | {s['net_max']:g} |")


if __name__ == "__main__":
    main()
