#!/usr/bin/env python3
"""Seuil de rentabilite (point mort), marge de securite et levier operationnel.

Exemples :
  python3 seuil_rentabilite.py --ca 120000000 --cv 78000000 --cf 30000000
  python3 seuil_rentabilite.py --ca 120000000 --cv 78000000 --cf 30000000 \
      --prix-unitaire 25000 --debut-exercice 2026-01-01
  # CA mensuel saisonnier (12 valeurs, meme taux de MCV) pour dater le point mort :
  python3 seuil_rentabilite.py --ca 120000000 --cv 78000000 --cf 30000000 \
      --ca-mensuel 6e6,6e6,8e6,10e6,12e6,12e6,10e6,8e6,10e6,12e6,14e6,12e6

Hypotheses : taux de MCV constant sur la periode, charges fixes de la periode entiere.
Sans --ca-mensuel, l'activite est supposee reguliere (annee de 360 jours, convention francaise).
"""
import argparse
import json
from datetime import date, timedelta


def main():
    p = argparse.ArgumentParser(description="Seuil de rentabilite et marge de securite")
    p.add_argument("--ca", type=float, required=True, help="chiffre d'affaires (ou PNB) de la periode")
    p.add_argument("--cv", type=float, required=True, help="charges variables de la periode")
    p.add_argument("--cf", type=float, required=True, help="charges fixes de la periode")
    p.add_argument("--prix-unitaire", type=float, help="prix de vente unitaire, pour le seuil en volume")
    p.add_argument("--debut-exercice", type=str, help="date de debut AAAA-MM-JJ, pour dater le point mort")
    p.add_argument("--ca-mensuel", type=str, help="12 CA mensuels separes par des virgules")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    mcv = a.ca - a.cv
    if mcv <= 0:
        raise SystemExit("MCV negative ou nulle : le point mort ne peut pas etre atteint.")
    taux_mcv = mcv / a.ca
    sr = a.cf / taux_mcv
    resultat = mcv - a.cf
    res = {
        "mcv": round(mcv),
        "taux_mcv_pct": round(taux_mcv * 100, 2),
        "resultat": round(resultat),
        "seuil_rentabilite_valeur": round(sr),
        "marge_securite": round(a.ca - sr),
        "indice_securite_pct": round((a.ca - sr) / a.ca * 100, 2),
        "levier_operationnel": round(mcv / resultat, 2) if resultat > 0 else None,
    }
    if a.prix_unitaire:
        res["seuil_rentabilite_volume"] = round(sr / a.prix_unitaire)

    if a.ca_mensuel:
        mois = [float(x) for x in a.ca_mensuel.split(",")]
        cumul, atteint = 0.0, None
        for i, m in enumerate(mois, 1):
            if cumul + m >= sr:
                atteint = (i, (sr - cumul) / m)  # fraction du mois i
                break
            cumul += m
        if atteint:
            res["point_mort_mois"] = atteint[0]
            res["point_mort_jour_du_mois"] = max(1, round(atteint[1] * 30))
        else:
            res["point_mort_mois"] = None
    else:
        jours = sr / a.ca * 360
        res["point_mort_jours_360"] = round(jours, 1)
        res["point_mort_mois"] = round(jours / 30, 2)
    if a.debut_exercice and res.get("point_mort_mois") is not None:
        d0 = date.fromisoformat(a.debut_exercice)
        if "point_mort_jours_360" in res:
            jours_civils = res["point_mort_jours_360"] * 365 / 360
        else:
            jours_civils = (res["point_mort_mois"] - 1) * 365 / 12 + res["point_mort_jour_du_mois"]
        res["date_point_mort"] = (d0 + timedelta(days=round(jours_civils))).isoformat()

    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return
    for k, v in res.items():
        if isinstance(v, (int, float)) and abs(v) >= 1000:
            v = f"{v:,.0f}".replace(",", " ")
        print(f"{k:<28}: {v}")
    if resultat <= 0:
        print("Attention : resultat negatif, le CA est sous le seuil de rentabilite.")


if __name__ == "__main__":
    main()
