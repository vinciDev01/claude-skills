#!/usr/bin/env python3
"""Normalise une balance exportée d'un ERP, d'Excel ou d'un core banking au format
compte;libelle;debit;credit;mouvement_debit attendu par les scripts des skills.

  debit / credit    : solde de clôture, ventilé en solde débiteur / solde créditeur
  mouvement_debit   : mouvements débit de la période (si l'export les contient)

Exemples :
  python3 normaliser_balance.py export.xlsx -o balance.csv --plan sfd
  python3 normaliser_balance.py export.csv -o balance.csv --plan syscohada --feuille "Balance"
  python3 normaliser_balance.py export.csv --apercu          # montre la détection sans écrire
  python3 normaliser_balance.py export.csv -o b.csv --col-compte "N° Cpte" --col-solde "Solde"

Le rapport de contrôle (JSON) est écrit sur la sortie standard, la balance dans -o.
"""
import argparse
import csv
import io
import json
import re
import sys
import unicodedata
from decimal import Decimal, InvalidOperation
from pathlib import Path

REFS = Path(__file__).resolve().parent.parent / "references"
PLANS = {"sfd": REFS / "plan-sfd-bceao.csv", "syscohada": REFS / "plan-comptable-syscohada-revise.csv"}
ZERO = Decimal("0")

# Synonymes d'en-têtes (comparés après normalisation : minuscules, sans accents ni ponctuation)
SYNONYMES = {
    "compte": ["compte", "n compte", "no compte", "numero compte", "numero de compte", "num compte",
               "n cpte", "cpte", "code compte", "account", "account number", "code", "compte general"],
    "libelle": ["libelle", "intitule", "libelle compte", "intitule compte", "designation", "description",
                "account name", "nom du compte", "libelle du compte"],
    "ouv_debit": ["solde ouverture debit", "a nouveau debit", "report debit", "ouverture debit", "an debit",
                  "solde initial debit", "debit ouverture"],
    "ouv_credit": ["solde ouverture credit", "a nouveau credit", "report credit", "ouverture credit", "an credit",
                   "solde initial credit", "credit ouverture"],
    "mvt_debit": ["mouvement debit", "mouvements debit", "mvt debit", "mvts debit", "debit periode",
                  "total debit", "cumul debit", "debit", "debits", "mouvements debiteurs", "debit mouvement"],
    "mvt_credit": ["mouvement credit", "mouvements credit", "mvt credit", "mvts credit", "credit periode",
                   "total credit", "cumul credit", "credit", "credits", "mouvements crediteurs", "credit mouvement"],
    "solde_debit": ["solde debit", "solde debiteur", "soldes debiteurs", "solde final debit", "solde fin debit",
                    "solde cloture debit", "sd"],
    "solde_credit": ["solde credit", "solde crediteur", "soldes crediteurs", "solde final credit", "solde fin credit",
                     "solde cloture credit", "sc"],
    "solde": ["solde", "solde final", "solde net", "solde cloture", "balance", "solde fin de periode"],
}
MOTS_SOUS_TOTAL = re.compile(r"\b(total|sous total|s/total|totaux|classe|report|a reporter|cumul classe)\b")


def norm(txt):
    txt = unicodedata.normalize("NFKD", str(txt or "")).encode("ascii", "ignore").decode().lower()
    txt = re.sub(r"[^a-z0-9/]+", " ", txt)
    return txt.strip()


def nombre(val):
    """Convertit '1 234 567,89', '(1 234)', '1234-', '1.234,5 D', 1234.5 en Decimal signé."""
    if val is None:
        return ZERO
    if isinstance(val, (int, float)):
        return Decimal(str(val))
    s = str(val).strip().replace(" ", "").replace(" ", "").replace(" ", "")
    if not s or s in ("-", "--"):
        return ZERO
    signe = 1
    if s.startswith("(") and s.endswith(")"):
        signe, s = -1, s[1:-1]
    if s.endswith("-"):
        signe, s = -signe, s[:-1]
    if s[-1:].upper() == "C" and re.match(r"^[\d.,]+C$", s, re.I):
        signe, s = -signe, s[:-1]
    elif s[-1:].upper() == "D" and re.match(r"^[\d.,]+D$", s, re.I):
        s = s[:-1]
    if "," in s and "." in s:  # le dernier séparateur est le séparateur décimal
        s = s.replace(".", "").replace(",", ".") if s.rfind(",") > s.rfind(".") else s.replace(",", "")
    elif s.count(",") > 1:          # 1,234,567 : virgules de milliers
        s = s.replace(",", "")
    elif "," in s:                  # 1234,56 : virgule décimale (convention française)
        s = s.replace(",", ".")
    elif s.count(".") > 1:          # 1.234.567 : points de milliers
        s = s.replace(".", "")
    try:
        return Decimal(s) * signe
    except InvalidOperation:
        return None


def lire_lignes(chemin, feuille):
    """Renvoie (lignes, info) ; chaque ligne est une liste de cellules."""
    ext = chemin.suffix.lower()
    if ext in (".xlsx", ".xlsm"):
        try:
            import openpyxl
        except ImportError:
            sys.exit("openpyxl absent : exporter la feuille en CSV ou installer openpyxl.")
        wb = openpyxl.load_workbook(chemin, read_only=True, data_only=True)
        ws = wb[feuille] if feuille else wb.worksheets[0]
        return [list(r) for r in ws.iter_rows(values_only=True)], {"format": "xlsx", "feuille": ws.title}
    if ext == ".xls":
        sys.exit("Format .xls (Excel 97) non lu : l'ouvrir dans Excel/LibreOffice et l'enregistrer en .xlsx ou .csv.")
    brut = chemin.read_bytes()
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            texte = brut.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    echantillon = "\n".join(texte.splitlines()[:30])
    delim = max([";", "\t", ",", "|"], key=lambda d: echantillon.count(d))
    lignes = list(csv.reader(io.StringIO(texte), delimiter=delim))
    return lignes, {"format": "csv", "encodage": enc, "separateur": delim}


def detecter_entete(lignes, forces):
    """Cherche dans les 30 premières lignes celle qui ressemble le plus à un en-tête."""
    meilleur = (0, None, {})
    for i, ligne in enumerate(lignes[:30]):
        cellules = [norm(c) for c in ligne]
        mapping = {}
        for role, syn in SYNONYMES.items():
            for j, c in enumerate(cellules):
                if c and c in syn and j not in mapping.values():
                    mapping.setdefault(role, j)
        # "debit"/"credit" seuls après des colonnes de solde : on garde la première occurrence = mouvements
        score = len(mapping) + (3 if "compte" in mapping else 0)
        if score > meilleur[0]:
            meilleur = (score, i, mapping)
    _, idx, mapping = meilleur
    if idx is None:
        idx, mapping = 0, {}
    entetes = [norm(c) for c in lignes[idx]] if lignes else []
    for role, nom in forces.items():
        if nom:
            n = norm(nom)
            if n not in entetes:
                sys.exit(f"Colonne forcée introuvable : {nom!r}. En-têtes lus : {lignes[idx]}")
            mapping[role] = entetes.index(n)
    return idx, mapping


def charger_plan(nom):
    if not nom:
        return None
    chemin = PLANS.get(nom, Path(nom))
    plan = {}
    with open(chemin, encoding="utf-8-sig") as f:
        lecteur = csv.reader(f, delimiter=";")
        next(lecteur, None)
        for r in lecteur:
            if r and r[0].strip():
                plan[r[0].strip()] = r[1].strip() if len(r) > 1 else ""
    return plan


def rattacher(compte, plan):
    """Renvoie (compte du plan, methode) : exact, zéros de fin retirés, ou préfixe le plus long."""
    if compte in plan:
        return compte, "exact"
    c = compte
    while c.endswith("0") and len(c) > 1:
        c = c[:-1]
        if c in plan:
            return c, "zeros_de_fin"
    chiffres = re.match(r"^\d+", compte)
    base = chiffres.group(0) if chiffres else compte
    for k in range(len(base), 0, -1):
        if base[:k] in plan:
            return base[:k], "prefixe"
    return None, "introuvable"


def main():
    ap = argparse.ArgumentParser(description="Normalise une balance au format des skills")
    ap.add_argument("fichier", type=Path)
    ap.add_argument("-o", "--sortie", type=Path, help="CSV normalisé à écrire")
    ap.add_argument("--plan", help="sfd, syscohada ou chemin d'un plan CSV (numero;libelle;...)")
    ap.add_argument("--feuille", help="nom de la feuille Excel")
    ap.add_argument("--apercu", action="store_true", help="affiche la détection sans écrire")
    ap.add_argument("--garder-sous-totaux", action="store_true")
    for role in ("compte", "libelle", "mvt_debit", "mvt_credit", "solde_debit", "solde_credit", "solde"):
        ap.add_argument(f"--col-{role.replace('_', '-')}", dest=f"col_{role}", help=f"nom exact de la colonne {role}")
    a = ap.parse_args()

    lignes, info = lire_lignes(a.fichier, a.feuille)
    forces = {r: getattr(a, f"col_{r}") for r in
              ("compte", "libelle", "mvt_debit", "mvt_credit", "solde_debit", "solde_credit", "solde")}
    idx, m = detecter_entete(lignes, forces)
    if "compte" not in m:
        sys.exit(f"Colonne du numéro de compte non détectée. En-têtes candidats : {lignes[idx] if lignes else []}. "
                 "Utiliser --col-compte \"Nom exact\".")

    if "solde_debit" in m or "solde_credit" in m:
        mode_solde = "colonnes_solde_debit_credit"
    elif "solde" in m:
        mode_solde = "colonne_solde_signee"
    elif "mvt_debit" in m and "mvt_credit" in m:
        mode_solde = "ouverture_plus_mouvements" if ("ouv_debit" in m or "ouv_credit" in m) else "mouvements_seuls"
    else:
        sys.exit(f"Aucune colonne de montant reconnue. Colonnes détectées : {m}. Forcer avec --col-solde, "
                 "--col-solde-debit/--col-solde-credit ou --col-mvt-debit/--col-mvt-credit.")

    cell = lambda r, role: r[m[role]] if role in m and m[role] < len(r) else None
    brutes, ecartees, illisibles = [], [], []
    for n, r in enumerate(lignes[idx + 1:], start=idx + 2):
        if not any(c not in (None, "") for c in r):
            continue
        valeur_compte = cell(r, "compte")
        if isinstance(valeur_compte, float) and valeur_compte.is_integer():
            valeur_compte = int(valeur_compte)  # compte saisi comme nombre dans Excel
        compte_brut = str(valeur_compte or "").strip()
        if re.fullmatch(r"\d+\.0", compte_brut):
            compte_brut = compte_brut[:-2]
        compte = re.sub(r"[\s.\-]", "", compte_brut)
        libelle = str(cell(r, "libelle") or "").strip()
        if not compte or not re.match(r"^\d", compte):
            ecartees.append({"ligne": n, "compte": compte_brut, "libelle": libelle, "motif": "pas de numero de compte"})
            continue
        if not a.garder_sous_totaux and MOTS_SOUS_TOTAL.search(norm(libelle)):
            ecartees.append({"ligne": n, "compte": compte, "libelle": libelle, "motif": "libelle de total"})
            continue
        vals = {k: nombre(cell(r, k)) for k in ("ouv_debit", "ouv_credit", "mvt_debit", "mvt_credit",
                                                 "solde_debit", "solde_credit", "solde")}
        if any(v is None for v in vals.values()):
            illisibles.append({"ligne": n, "compte": compte, "valeurs": [str(cell(r, k)) for k in m]})
            continue
        if mode_solde == "colonnes_solde_debit_credit":
            solde = vals["solde_debit"] - vals["solde_credit"]
        elif mode_solde == "colonne_solde_signee":
            solde = vals["solde"]
        else:
            solde = vals["ouv_debit"] - vals["ouv_credit"] + vals["mvt_debit"] - vals["mvt_credit"]
        brutes.append({"ligne": n, "compte": compte, "libelle": libelle, "solde": solde,
                       "mvtd": vals["mvt_debit"] if "mvt_debit" in m else None})

    # Comptes parents présents en même temps que leurs sous-comptes = sous-totaux hiérarchiques
    comptes = {b["compte"] for b in brutes}
    parents = set()
    if not a.garder_sous_totaux:
        for c in comptes:
            enfants = [b for b in brutes if b["compte"] != c and b["compte"].startswith(c)]
            if enfants:
                somme = sum(b["solde"] for b in enfants)
                parent = sum(b["solde"] for b in brutes if b["compte"] == c)
                if parent == somme:
                    parents.add(c)
        for b in [b for b in brutes if b["compte"] in parents]:
            ecartees.append({"ligne": b["ligne"], "compte": b["compte"], "libelle": b["libelle"],
                             "motif": "compte parent egal a la somme de ses sous-comptes"})
        brutes = [b for b in brutes if b["compte"] not in parents]

    plan = charger_plan(a.plan)
    rattachements, introuvables, sortie = {}, [], {}
    for b in brutes:
        cible, methode = (b["compte"], "sans_plan") if plan is None else rattacher(b["compte"], plan)
        if cible is None:
            introuvables.append({"ligne": b["ligne"], "compte": b["compte"], "libelle": b["libelle"],
                                 "solde": str(b["solde"])})
            cible = b["compte"]
        elif methode not in ("exact", "sans_plan"):
            rattachements.setdefault(f"{b['compte']} -> {cible}", methode)
        s = sortie.setdefault(cible, {"libelle": (plan or {}).get(cible) or b["libelle"], "solde": ZERO,
                                      "mvtd": ZERO, "a_mvtd": False})
        s["solde"] += b["solde"]
        if b["mvtd"] is not None:
            s["mvtd"] += b["mvtd"]
            s["a_mvtd"] = True

    total_d = sum(s["solde"] for s in sortie.values() if s["solde"] > 0)
    total_c = -sum(s["solde"] for s in sortie.values() if s["solde"] < 0)
    rapport = {
        "fichier": str(a.fichier), **info,
        "ligne_entete": idx + 1,
        "colonnes_detectees": {k: (lignes[idx][v] if v < len(lignes[idx]) else v) for k, v in m.items()},
        "calcul_du_solde": mode_solde,
        "lignes_retenues": len(brutes),
        "comptes_en_sortie": len(sortie),
        "total_soldes_debiteurs": str(total_d),
        "total_soldes_crediteurs": str(total_c),
        "equilibre": total_d == total_c,
        "ecart": str(total_d - total_c),
        "lignes_ecartees": ecartees,
        "lignes_illisibles": illisibles,
        "rattachements_au_plan": rattachements,
        "comptes_hors_plan": introuvables,
    }
    if mode_solde == "mouvements_seuls":
        rapport["avertissement"] = ("Pas de soldes d'ouverture détectés : le solde est calculé sur les seuls "
                                    "mouvements. Vérifier que l'export inclut les à-nouveaux.")

    if not a.apercu:
        if not a.sortie:
            sys.exit("Préciser le fichier de sortie avec -o (ou utiliser --apercu).")
        avec_mvtd = any(s["a_mvtd"] for s in sortie.values())
        with open(a.sortie, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["compte", "libelle", "debit", "credit"] + (["mouvement_debit"] if avec_mvtd else []))
            for c in sorted(sortie):
                s = sortie[c]
                ligne = [c, s["libelle"], str(max(s["solde"], ZERO)), str(max(-s["solde"], ZERO))]
                w.writerow(ligne + ([str(s["mvtd"])] if avec_mvtd else []))
        rapport["sortie"] = str(a.sortie)
    print(json.dumps(rapport, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
