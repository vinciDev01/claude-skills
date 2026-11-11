#!/usr/bin/env python3
"""Bulletin de paie Togo (secteur privé) : CNSS, AMU, IRPP, net à payer, coût employeur, écritures.

Les taux et le barème sont lus dans references/parametres-paie-togo.json (sources et date de
vérification dans ce fichier). Mettre ce fichier à jour à chaque loi de finances.

Exemples :
  python3 calcul_paie_togo.py 450000 --charges 3
  python3 calcul_paie_togo.py 300000 --primes 50000 --frais 20000 --charges 2 --json

Méthode IRPP : le salaire imposable mensuel est annualisé (x 12), l'impôt annuel est calculé
selon le barème (art. 74 CGI) puis divisé par 12 pour la retenue mensuelle.
"""
import argparse
import json
import math
import sys
from pathlib import Path

PARAMS = Path(__file__).resolve().parent.parent / "references" / "parametres-paie-togo.json"


def arrondi_bas(x, pas):
    return math.floor(x / pas) * pas


def irpp_annuel(revenu, bareme):
    impot, bas = 0.0, 0
    for tranche in bareme:
        haut = tranche["jusqu_a"]
        if haut is None or revenu <= haut:
            impot += (revenu - bas) * tranche["taux"]
            break
        impot += (haut - bas) * tranche["taux"]
        bas = haut
    return impot


def calculer(base, primes, frais, charges, p):
    smig = p["smig_mensuel"]["valeur"]
    brut = base + primes                      # brut imposable et soumis à cotisations
    assiette = max(brut, smig)                # plancher SMIG (CNSS et AMU)
    cn, amu, ir = p["cnss"], p["amu"], p["irpp"]

    cnss_sal = assiette * cn["taux_salarial"]
    amu_sal = assiette * amu["taux_salarial"]
    cnss_pat_detail = {k: assiette * t for k, t in cn["taux_patronal"].items()}
    cnss_pat = sum(cnss_pat_detail.values())
    amu_pat = assiette * amu["taux_patronal"]

    # IRPP (annuel)
    brut_an = brut * 12
    retraite_an = min(cnss_sal * 12, brut_an * ir["limite_deduction_retraite_pct_brut"])
    apres_cotis = brut_an - retraite_an - amu_sal * 12
    ab = ir["abattement_frais_pro"]
    abattement = min(apres_cotis, ab["plafond_base_annuelle"]) * ab["taux"]
    cf = ir["charges_de_famille"]
    nb = min(charges, cf["max_personnes"])
    deduc_famille = nb * cf["montant_annuel_par_personne"]
    imposable = arrondi_bas(max(0.0, apres_cotis - abattement - deduc_famille), ir["arrondi_revenu"])
    impot_an = arrondi_bas(irpp_annuel(imposable, ir["bareme_annuel"]), ir["arrondi_impot"])
    irpp_mois = round(impot_an / 12)

    cnss_sal, amu_sal = round(cnss_sal), round(amu_sal)
    cnss_pat, amu_pat = round(cnss_pat), round(amu_pat)
    net = brut - cnss_sal - amu_sal - irpp_mois + frais
    cout = brut + frais + cnss_pat + amu_pat

    ecritures = {
        "salaire": [
            ("661", "Rémunérations directes versées au personnel national", brut, 0),
            ("431", "Sécurité sociale (CNSS salariale)", 0, cnss_sal),
            ("433", "Autres organismes sociaux (AMU salariale)", 0, amu_sal),
            ("4472", "Impôts sur salaires (IRPP)", 0, irpp_mois),
            ("422", "Personnel, rémunérations dues", 0, brut - cnss_sal - amu_sal - irpp_mois),
        ],
        "charges_patronales": [
            ("664", "Charges sociales", cnss_pat + amu_pat, 0),
            ("431", "Sécurité sociale (CNSS patronale)", 0, cnss_pat),
            ("433", "Autres organismes sociaux (AMU patronale)", 0, amu_pat),
        ],
    }
    if frais:
        ecritures["remboursement_frais"] = [
            ("6", "Compte de charge par nature (selon la dépense remboursée)", frais, 0),
            ("422", "Personnel, rémunérations dues", 0, frais),
        ]

    return {
        "brut_mensuel": brut,
        "assiette_cotisations": assiette,
        "cnss_salariale": cnss_sal,
        "amu_salariale": amu_sal,
        "irpp": {
            "brut_annuel": brut_an,
            "cotisations_deduites_annuelles": round(retraite_an + amu_sal * 12),
            "abattement_frais_pro_28": round(abattement),
            "personnes_a_charge_retenues": nb,
            "deduction_charges_famille": deduc_famille,
            "revenu_net_imposable_annuel": imposable,
            "impot_annuel": impot_an,
            "retenue_mensuelle": irpp_mois,
        },
        "remboursement_frais_non_soumis": frais,
        "net_a_payer": round(net),
        "cnss_patronale": cnss_pat,
        "cnss_patronale_detail": {k: round(v) for k, v in cnss_pat_detail.items()},
        "amu_patronale": amu_pat,
        "cout_total_employeur": round(cout),
        "a_reverser": {"CNSS": cnss_sal + cnss_pat, "AMU (via CNSS)": amu_sal + amu_pat, "OTR (IRPP)": irpp_mois},
        "ecritures": ecritures,
        "parametres_verifies_le": p["_meta"]["verifie_le"],
    }


def main():
    a = argparse.ArgumentParser(description="Calcul de paie Togo (CNSS, AMU, IRPP)")
    a.add_argument("salaire_base", type=float, help="salaire de base mensuel (FCFA)")
    a.add_argument("--primes", type=float, default=0, help="primes et indemnités imposables mensuelles")
    a.add_argument("--frais", type=float, default=0,
                   help="remboursements de frais justifiés (non imposables, hors cotisations)")
    a.add_argument("--charges", type=int, default=0,
                   help="personnes à charge au sens de l'art. 72 CGI (conjoint sans revenu, enfants...), max 6")
    a.add_argument("--params", type=Path, default=PARAMS, help="fichier de paramètres JSON")
    a.add_argument("--json", action="store_true")
    args = a.parse_args()

    p = json.loads(args.params.read_text(encoding="utf-8"))
    r = calculer(args.salaire_base, args.primes, args.frais, args.charges, p)
    if r["brut_mensuel"] < p["smig_mensuel"]["valeur"]:
        print(f"Attention : brut inférieur au SMIG ({p['smig_mensuel']['valeur']} FCFA).", file=sys.stderr)

    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return

    f = lambda v: f"{v:,.0f}".replace(",", " ")
    i = r["irpp"]
    print(f"Brut mensuel                 : {f(r['brut_mensuel'])}")
    print(f"CNSS salariale (4 %)         : {f(r['cnss_salariale'])}")
    print(f"AMU salariale (5 %)          : {f(r['amu_salariale'])}")
    print(f"IRPP mensuel                 : {f(i['retenue_mensuelle'])}")
    if r["remboursement_frais_non_soumis"]:
        print(f"Remboursement de frais       : {f(r['remboursement_frais_non_soumis'])}")
    print(f"NET A PAYER                  : {f(r['net_a_payer'])}")
    print()
    print(f"CNSS patronale (17,5 %)      : {f(r['cnss_patronale'])}")
    print(f"AMU patronale (5 %)          : {f(r['amu_patronale'])}")
    print(f"COUT TOTAL EMPLOYEUR         : {f(r['cout_total_employeur'])}")
    print()
    print("Détail IRPP annuel :")
    for k in ("brut_annuel", "cotisations_deduites_annuelles", "abattement_frais_pro_28",
              "deduction_charges_famille", "revenu_net_imposable_annuel", "impot_annuel"):
        print(f"  {k:<32}: {f(i[k])}")
    print(f"  personnes_a_charge_retenues     : {i['personnes_a_charge_retenues']}")
    print()
    for nom, lignes in r["ecritures"].items():
        print(f"Écriture {nom} :")
        for c, lib, d, cr in lignes:
            print(f"  {c:<5} {lib:<58} {f(d) if d else '':>12} {f(cr) if cr else '':>12}")
    print(f"\nParamètres vérifiés le {r['parametres_verifies_le']} (references/parametres-paie-togo.json).")


if __name__ == "__main__":
    main()
