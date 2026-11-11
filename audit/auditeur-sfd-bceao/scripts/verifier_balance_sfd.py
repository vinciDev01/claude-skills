import csv
import json
import sys
from decimal import Decimal
from pathlib import Path

def charger_plan(chemin_plan: Path) -> dict:
    plan = {}
    with open(chemin_plan, mode="r", encoding="utf-8-sig") as f:
        lecteur = csv.DictReader(f, delimiter=";")
        for ligne in lecteur:
            num = ligne["numero"].strip()
            plan[num] = {
                "libelle": ligne["libelle"].strip(),
                "nature": ligne["nature"].strip(),
                "collectif": ligne["collectif"].strip().lower() == "true"
            }
    return plan

def auditer_balance(chemin_balance: Path, chemin_plan: Path) -> dict:
    plan = charger_plan(chemin_plan)
    total_debit = Decimal("0")
    total_credit = Decimal("0")
    anomalies = []
    soldes_par_compte = {}

    with open(chemin_balance, mode="r", encoding="utf-8-sig") as f:
        lecteur = csv.DictReader(f, delimiter=";")
        for ligne in lecteur:
            compte = ligne["compte"].strip()
            debit = Decimal(ligne.get("debit", "0").replace(" ", "").replace(",", ".") or "0")
            credit = Decimal(ligne.get("credit", "0").replace(" ", "").replace(",", ".") or "0")

            total_debit += debit
            total_credit += credit
            solde = debit - credit
            soldes_par_compte[compte] = str(solde)

            # 1. Verification de l'existence dans le plan SFD-BCEAO
            if compte not in plan:
                anomalies.append({
                    "type": "COMPTE_HORS_PLAN",
                    "compte": compte,
                    "detail": "Ce numero de compte n'existe pas dans plan-sfd-bceao.csv"
                })
                continue

            nature = plan[compte]["nature"]

            # 2. Detection des soldes inverses anormaux
            if compte.startswith("101") and solde < 0:
                anomalies.append({
                    "type": "CAISSE_CREDITRICE",
                    "compte": compte,
                    "montant": str(solde),
                    "detail": "Solde de caisse crediteur (anomalie critique d'audit)"
                })
            elif compte.startswith("379") and solde != 0:
                anomalies.append({
                    "type": "COMPTE_ATTENTE_NON_SOLDE",
                    "compte": compte,
                    "montant": str(solde),
                    "detail": "Compte d'attente (3791/3792) non apure avant arrete"
                })
            elif nature == "ACTIF" and solde < 0 and not compte.endswith("9") and not compte.endswith("8"):
                anomalies.append({
                    "type": "ACTIF_CREDITEUR",
                    "compte": compte,
                    "montant": str(solde),
                    "detail": "Compte d'actif presentant un solde crediteur a reclasser"
                })
            elif nature == "PASSIF" and solde > 0 and not compte.startswith("573"):
                anomalies.append({
                    "type": "PASSIF_DEBITEUR",
                    "compte": compte,
                    "montant": str(solde),
                    "detail": "Compte de passif presentant un solde debiteur a justifier"
                })

    equilibre = (total_debit == total_credit)
    if not equilibre:
        anomalies.insert(0, {
            "type": "DESEQUILIBRE_BALANCE",
            "ecart": str(total_debit - total_credit),
            "detail": "Total Debit different du Total Credit"
        })

    return {
        "equilibre": equilibre,
        "total_debit": str(total_debit),
        "total_credit": str(total_credit),
        "nombre_anomalies": len(anomalies),
        "anomalies": anomalies
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verifier_balance_sfd.py <chemin_balance.csv>")
        sys.exit(1)

    dossier_skill = Path(__file__).resolve().parent.parent
    fichier_balance = Path(sys.argv[1])
    fichier_plan = dossier_skill / "references" / "plan-sfd-bceao.csv"

    resultat = auditer_balance(fichier_balance, fichier_plan)
    print(json.dumps(resultat, indent=2, ensure_ascii=False))
