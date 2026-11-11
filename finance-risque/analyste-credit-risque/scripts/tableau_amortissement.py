#!/usr/bin/env python3
"""Echeancier de pret, TEG et DSCR.

Exemples :
  python3 tableau_amortissement.py 15000000 14 24
  python3 tableau_amortissement.py 15000000 14 24 --mode constant --differe 3 \
      --frais-dossier 150000 --assurance-mensuelle 7500 --cash-flow 1100000
  python3 tableau_amortissement.py 2000000 24 12 --periodicite 4 --json

Conventions :
  - taux nominal annuel, taux periodique = taux / periodes par an (taux proportionnel) ;
  - differe partiel : seuls les interets sont payes pendant le differe ;
  - TEG proportionnel = taux periodique interne x periodes par an (convention usuelle UEMOA) ;
  - TEG actuariel = (1 + taux periodique interne) ^ periodes par an - 1, donne pour information.
"""
import argparse
import json
import sys


def echeancier(montant, taux_annuel, nb_echeances, periodes_an, mode, differe):
    t = taux_annuel / 100 / periodes_an
    lignes = []
    crd = montant
    for k in range(1, differe + 1):
        interet = crd * t
        lignes.append((k, crd, interet, 0.0, interet, crd))
    n = nb_echeances - differe
    if n <= 0:
        raise ValueError("le differe doit etre inferieur au nombre d'echeances")
    if mode == "annuite":
        ech = montant * t / (1 - (1 + t) ** -n) if t else montant / n
    for k in range(1, n + 1):
        interet = crd * t
        if mode == "annuite":
            capital = ech - interet
        else:
            capital = montant / n
        if k == n:
            capital = crd  # solde exact sur la derniere echeance
        total = capital + interet
        lignes.append((differe + k, crd, interet, capital, total, crd - capital))
        crd -= capital
    return lignes


def taux_interne(flux_net, flux):
    """Taux periodique r tel que flux_net = somme(flux_k / (1+r)^k). Dichotomie."""
    bas, haut = 0.0, 1.0
    for _ in range(200):
        r = (bas + haut) / 2
        va = sum(f / (1 + r) ** (k + 1) for k, f in enumerate(flux))
        if va > flux_net:
            bas = r
        else:
            haut = r
    return (bas + haut) / 2


def main():
    p = argparse.ArgumentParser(description="Echeancier de pret, TEG et DSCR")
    p.add_argument("montant", type=float, help="capital emprunte (FCFA)")
    p.add_argument("taux", type=float, help="taux nominal annuel en %% (ex. 14)")
    p.add_argument("echeances", type=int, help="nombre total d'echeances (differe compris)")
    p.add_argument("--periodicite", type=int, default=12,
                   help="echeances par an : 12 mensuel, 4 trimestriel, 2 semestriel, 1 annuel")
    p.add_argument("--mode", choices=["annuite", "constant"], default="annuite",
                   help="annuites constantes (defaut) ou amortissement constant du capital")
    p.add_argument("--differe", type=int, default=0, help="echeances de differe partiel (interets seuls)")
    p.add_argument("--frais-dossier", type=float, default=0.0, help="frais preleves au decaissement")
    p.add_argument("--assurance-mensuelle", type=float, default=0.0,
                   help="assurance ou commission fixe ajoutee a chaque echeance")
    p.add_argument("--cash-flow", type=float, default=None,
                   help="cash-flow net disponible par periode, pour le DSCR")
    p.add_argument("--json", action="store_true", help="sortie JSON")
    a = p.parse_args()

    lignes = echeancier(a.montant, a.taux, a.echeances, a.periodicite, a.mode, a.differe)
    flux = [l[4] + a.assurance_mensuelle for l in lignes]
    net = a.montant - a.frais_dossier
    r = taux_interne(net, flux)
    teg_prop = r * a.periodicite * 100
    teg_act = ((1 + r) ** a.periodicite - 1) * 100
    total_interets = sum(l[2] for l in lignes)
    ech_max = max(flux)
    res = {
        "parametres": vars(a),
        "total_interets": round(total_interets),
        "cout_total_credit": round(total_interets + a.frais_dossier + a.assurance_mensuelle * len(lignes)),
        "echeance_max": round(ech_max),
        "teg_proportionnel_pct": round(teg_prop, 2),
        "teg_actuariel_pct": round(teg_act, 2),
        "echeancier": [
            {"n": l[0], "crd_debut": round(l[1]), "interet": round(l[2]), "capital": round(l[3]),
             "echeance": round(l[4] + a.assurance_mensuelle), "crd_fin": round(l[5])}
            for l in lignes
        ],
    }
    if a.cash_flow is not None:
        res["dscr"] = round(a.cash_flow / ech_max, 2)

    if a.json:
        json.dump(res, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return
    print(f"{'N':>3} {'CRD debut':>14} {'Interet':>12} {'Capital':>12} {'Echeance':>12} {'CRD fin':>14}")
    for e in res["echeancier"]:
        print(f"{e['n']:>3} {e['crd_debut']:>14,} {e['interet']:>12,} {e['capital']:>12,} "
              f"{e['echeance']:>12,} {e['crd_fin']:>14,}".replace(",", " "))
    print()
    print(f"Total interets       : {res['total_interets']:,}".replace(",", " "))
    print(f"Cout total du credit : {res['cout_total_credit']:,}".replace(",", " "))
    print(f"TEG proportionnel    : {res['teg_proportionnel_pct']} %")
    print(f"TEG actuariel        : {res['teg_actuariel_pct']} %")
    if "dscr" in res:
        print(f"DSCR (cash-flow / echeance max) : {res['dscr']}x")


if __name__ == "__main__":
    main()
