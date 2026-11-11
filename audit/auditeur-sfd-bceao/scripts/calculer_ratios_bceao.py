#!/usr/bin/env python3
"""Calcul des etats et ratios prudentiels SFD-BCEAO a partir d'une balance CSV.

Usage :
    python calculer_ratios_bceao.py balance.csv [grandeurs.json] [--n1 balance_n1.csv] [--refs dossier]
"""
import argparse
import csv
import json
import re
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

ZERO = Decimal("0")

# Sens du solde selon la cote du poste dans lequel la formule est ecrite.
# SOLDE(x) = debit - credit pour un poste ACTIF ou CHARGE, credit - debit pour un
# poste PASSIF ou PRODUIT. C'est ce qui fait que les comptes d'amortissement et de
# provisions (ex. 4319) se deduisent tout seuls dans un poste d'actif, et que
# L80 = SOLDE(59) + SOLDE(6) + SOLDE(7) donne bien produits - charges.
SENS_PAR_COTE = {"ACTIF": "DEBIT", "CHARGE": "DEBIT", "PASSIF": "CREDIT", "PRODUIT": "CREDIT"}
# Repli quand le poste n'a pas de cote (ratios, postes "AUCUN") : sens naturel du compte.
PREFIXES_CREDIT = ("15", "16", "17", "18", "25", "27", "5", "7")

FONCTIONS = ("PLAGE", "POSTE", "GRANDEUR", "SOLDE", "DEB", "CRED", "MVTD", "POSITIF", "NEGATIF", "MOYENNE")
RE_APPEL = re.compile(r"\b(" + "|".join(FONCTIONS) + r")\(")


def nettoyer_nombre(valeur) -> Decimal:
    if valeur is None or valeur == "":
        return ZERO
    if isinstance(valeur, Decimal):
        return valeur
    if isinstance(valeur, (int, float)):
        return Decimal(str(valeur))
    propre = str(valeur).replace(" ", "").replace("\u00a0", "").replace(",", ".")
    try:
        return Decimal(propre)
    except InvalidOperation:
        return ZERO


def charger_balance(chemin: Path) -> dict:
    """Charge la balance (compte;libelle;debit;credit[;mouvement_debit]).

    Les lignes d'un meme compte sont cumulees. Sans colonne mouvement_debit,
    le mouvement debit est assimile au debit.
    """
    comptes = {}
    with open(chemin, mode="r", encoding="utf-8-sig") as f:
        lecteur = csv.DictReader(f, delimiter=";")
        for brute in lecteur:
            ligne = {(k or "").strip().lower(): v for k, v in brute.items()}
            compte = (ligne.get("compte") or "").strip()
            if not compte:
                continue
            debit = nettoyer_nombre(ligne.get("debit"))
            credit = nettoyer_nombre(ligne.get("credit"))
            mvtd = nettoyer_nombre(ligne.get("mouvement_debit")) if ligne.get("mouvement_debit") not in (None, "") else debit
            c = comptes.setdefault(compte, {"debit": ZERO, "credit": ZERO, "mvtd": ZERO})
            c["debit"] += debit
            c["credit"] += credit
            c["mvtd"] += mvtd
    return comptes


def charger_grandeurs(chemin: Path):
    """Retourne (grandeurs, statut, avertissements).

    Formats acceptes : {"grandeurs": {...}, "statut": {...}}, un dict code -> valeur,
    ou une liste d'objets {"code": ..., "valeur": ...}. Un simple catalogue de
    definitions (sans valeurs) est signale et ignore.
    """
    with open(chemin, mode="r", encoding="utf-8") as f:
        contenu = json.load(f)
    avertissements = []
    statut = {}
    if isinstance(contenu, list):
        if contenu and all("valeur" in g for g in contenu):
            return {g["code"]: g["valeur"] for g in contenu}, statut, avertissements
        avertissements.append(
            f"{chemin.name} est un catalogue de definitions sans valeurs : toutes les grandeurs sont a 0"
        )
        return {}, statut, avertissements
    statut = contenu.get("statut", {})
    grandeurs = contenu.get("grandeurs", {k: v for k, v in contenu.items() if k != "statut"})
    return grandeurs, statut, avertissements


def sens_par_defaut(prefixe: str) -> str:
    return "CREDIT" if prefixe.startswith(PREFIXES_CREDIT) else "DEBIT"


def _extraire_appel(expr: str, debut_nom: int, fin_nom: int):
    """Retourne (index de la parenthese fermante, texte de l'argument) en respectant l'imbrication."""
    profondeur = 1
    i = fin_nom
    while i < len(expr):
        if expr[i] == "(":
            profondeur += 1
        elif expr[i] == ")":
            profondeur -= 1
            if profondeur == 0:
                return i, expr[fin_nom:i]
        i += 1
    raise ValueError(f"Parenthese non fermee dans : {expr}")


def _fmt(valeur: Decimal) -> str:
    """Nombre entre parentheses, jamais en notation scientifique (evite '1E+7' et 'a - -b')."""
    return "(" + format(valeur, "f") + ")"


def eval_arithmetique(expr: str) -> Decimal:
    """Evalue + - * / et parentheses en Decimal, sans eval(). Division par zero -> ValueError."""
    texte = expr.replace(" ", "")
    jetons = re.findall(r"\d+(?:\.\d+)?|[()+\-*/]", texte)
    if "".join(jetons) != texte:
        raise ValueError(f"Caracteres inattendus dans l'expression : {expr}")
    pos = 0

    def courant():
        return jetons[pos] if pos < len(jetons) else None

    def expression():
        nonlocal pos
        v = terme()
        while courant() in ("+", "-"):
            op = jetons[pos]
            pos += 1
            w = terme()
            v = v + w if op == "+" else v - w
        return v

    def terme():
        nonlocal pos
        v = facteur()
        while courant() in ("*", "/"):
            op = jetons[pos]
            pos += 1
            w = facteur()
            if op == "*":
                v = v * w
            else:
                if w == 0:
                    raise ValueError("Division par zero")
                v = v / w
        return v

    def facteur():
        nonlocal pos
        j = courant()
        if j in ("+", "-"):
            pos += 1
            v = facteur()
            return -v if j == "-" else v
        if j == "(":
            pos += 1
            v = expression()
            if courant() != ")":
                raise ValueError(f"Parenthese manquante : {expr}")
            pos += 1
            return v
        if j is None:
            raise ValueError(f"Expression incomplete : {expr}")
        pos += 1
        return Decimal(j)

    if not jetons:
        return ZERO
    resultat = expression()
    if pos != len(jetons):
        raise ValueError(f"Expression invalide : {expr}")
    return resultat


class MoteurBCEAO:
    FICHIERS_REFERENCE = [
        "DIMF2000_BILAN_DEV.json",
        "DIMF2080_RESULTAT_DEV.json",
        "FONDS_PROPRES.json",
        "RATIOS_PRUDENTIELS_010_016.json",
        "INDICATEURS_FINANCIERS_020.json",
    ]

    def __init__(self, dossier_refs: Path, comptes: dict, grandeurs: dict, statut_sfd: dict, moteur_n1=None):
        self.comptes = comptes
        self.grandeurs = {k: nettoyer_nombre(v) for k, v in grandeurs.items()}
        self.statut_sfd = statut_sfd
        self.moteur_n1 = moteur_n1
        self.tableaux = {}
        self.index_postes = {}
        self.cache_postes = {}
        self._en_cours = set()
        self.grandeurs_manquantes = set()
        self.avertissements = set()

        for nom in self.FICHIERS_REFERENCE:
            chemin = dossier_refs / nom
            if not chemin.exists():
                self.avertissements.add(f"Referentiel introuvable : {nom}")
                continue
            with open(chemin, mode="r", encoding="utf-8") as f:
                data = json.load(f)
            self.tableaux[data["code"]] = data
            self.index_postes[data["code"]] = {p["code"]: p for p in data["definition"].get("postes", [])}

    # ---------- comptes ----------
    def eval_fonction_compte(self, func: str, prefixe: str, cote: str = None) -> Decimal:
        """SOLDE / DEB / CRED / MVTD sur tous les comptes commencant par prefixe."""
        total = ZERO
        trouve = False
        for code, m in self.comptes.items():
            if not code.startswith(prefixe):
                continue
            trouve = True
            solde_deb = m["debit"] - m["credit"]
            if func == "DEB":
                total += max(ZERO, solde_deb)
            elif func == "CRED":
                total += max(ZERO, -solde_deb)
            elif func == "MVTD":
                total += m["mvtd"]
            else:  # SOLDE
                sens = SENS_PAR_COTE.get(cote) or sens_par_defaut(prefixe)
                total += solde_deb if sens == "DEBIT" else -solde_deb
        return total if trouve else ZERO

    # ---------- postes ----------
    def get_poste(self, code_tableau: str, code_poste: str, colonne: str = None) -> Decimal:
        tableau = self.tableaux.get(code_tableau)
        if not tableau:
            self.avertissements.add(f"Tableau inconnu : {code_tableau}")
            return ZERO
        col = colonne or tableau["definition"]["colonnePrincipale"]
        cle = (code_tableau, code_poste, col)
        if cle in self.cache_postes:
            return self.cache_postes[cle]
        poste = self.index_postes[code_tableau].get(code_poste)
        if poste is None:
            self.avertissements.add(f"Poste inconnu : {code_tableau}:{code_poste}")
            return ZERO
        if cle in self._en_cours:
            raise ValueError(f"Reference circulaire sur {code_tableau}:{code_poste}:{col}")
        self._en_cours.add(cle)
        try:
            formule = poste.get("formules", {}).get(col, "")
            valeur = self.evaluer_expression(formule, code_tableau, col, poste.get("cote"))
        finally:
            self._en_cours.discard(cle)
        self.cache_postes[cle] = valeur
        return valeur

    def _plage(self, arg: str, code_tableau: str, col: str) -> Decimal:
        """PLAGE(debut, fin) : somme des postes de meme niveau que 'debut' entre les deux bornes."""
        debut, fin = [x.strip() for x in arg.split(",")]
        postes = self.tableaux[code_tableau]["definition"]["postes"]
        codes = [p["code"] for p in postes]
        if debut not in codes or fin not in codes:
            self.avertissements.add(f"PLAGE({debut},{fin}) : borne inconnue dans {code_tableau}")
            return ZERO
        i_deb, i_fin = codes.index(debut), codes.index(fin)
        niveau_ref = postes[i_deb]["niveau"]
        somme = ZERO
        for p in postes[i_deb : i_fin + 1]:
            if p["niveau"] == niveau_ref and p.get("formules"):
                somme += self.get_poste(code_tableau, p["code"], col)
        return somme

    def _poste_ref(self, arg: str, code_tableau: str, col_courante: str) -> Decimal:
        """POSTE(TAB:CODE, COL) ou POSTE(CODE). Sans colonne : meme colonne dans le meme tableau, sinon colonne principale."""
        parties = [x.strip() for x in arg.split(",")]
        ref = parties[0]
        col = parties[1] if len(parties) > 1 else None
        if ":" in ref:
            tab, code_p = ref.split(":", 1)
        else:
            tab, code_p = code_tableau, ref
        if col is None and tab == code_tableau:
            tableau = self.tableaux[tab]["definition"]
            if any(c["code"] == col_courante for c in tableau["colonnes"]):
                col = col_courante
        return self.get_poste(tab, code_p, col)

    # ---------- expressions ----------
    def evaluer_expression(self, expr: str, code_tableau: str, col_courante: str, cote: str = None) -> Decimal:
        if not expr or not expr.strip():
            return ZERO
        while True:
            m = RE_APPEL.search(expr)
            if not m:
                break
            nom = m.group(1)
            fin_parenthese, arg = _extraire_appel(expr, m.start(), m.end())
            if nom == "PLAGE":
                val = self._plage(arg, code_tableau, col_courante)
            elif nom == "POSTE":
                val = self._poste_ref(arg, code_tableau, col_courante)
            elif nom == "GRANDEUR":
                code_g = arg.strip()
                if code_g not in self.grandeurs:
                    self.grandeurs_manquantes.add(code_g)
                val = self.grandeurs.get(code_g, ZERO)
            elif nom in ("SOLDE", "DEB", "CRED", "MVTD"):
                val = self.eval_fonction_compte(nom, arg.strip(), cote)
            elif nom == "POSITIF":
                val = max(ZERO, self.evaluer_expression(arg, code_tableau, col_courante, cote))
            elif nom == "NEGATIF":
                val = abs(min(ZERO, self.evaluer_expression(arg, code_tableau, col_courante, cote)))
            else:  # MOYENNE : moyenne N et N-1 si une balance N-1 est fournie
                val_n = self.evaluer_expression(arg, code_tableau, col_courante, cote)
                if self.moteur_n1 is not None:
                    val_n1 = self.moteur_n1.evaluer_expression(arg, code_tableau, col_courante, cote)
                    val = (val_n + val_n1) / 2
                else:
                    self.avertissements.add("MOYENNE calculee sur N seul : fournir --n1 balance_n1.csv pour la vraie moyenne")
                    val = val_n
            expr = expr[: m.start()] + _fmt(val) + expr[fin_parenthese + 1 :]
        try:
            return eval_arithmetique(expr)
        except ValueError as e:
            self.avertissements.add(f"Expression non evaluee ({e}) -> 0")
            return ZERO

    # ---------- normes ----------
    def verifier_norme(self, valeur, normes: list) -> dict:
        if not normes:
            return {"norme": "Aucune", "ecart": None, "conforme": None}
        retenue = None
        for n in normes:
            cond = n.get("condition")
            if not cond or all(v is None or self.statut_sfd.get(k) == v for k, v in cond.items()):
                retenue = n
                break
        if retenue is None:
            return {"norme": "Aucune applicable", "ecart": None, "conforme": None}
        seuil = retenue.get("valeur")
        if seuil is None:
            return {"norme": retenue["type"], "ecart": None, "conforme": None}
        seuil = Decimal(str(seuil))
        stricte = retenue.get("stricte", False)
        if retenue["type"] == "MAXIMUM":
            conforme = valeur < seuil if stricte else valeur <= seuil
            libelle = f"{'<' if stricte else '<='} {seuil}"
        elif retenue["type"] == "MINIMUM":
            conforme = valeur > seuil if stricte else valeur >= seuil
            libelle = f"{'>' if stricte else '>='} {seuil}"
        else:
            return {"norme": retenue["type"], "ecart": None, "conforme": None}
        return {"norme": libelle, "ecart": str(valeur - seuil), "conforme": conforme}

    # ---------- audit ----------
    def _ratios(self, code_tab: str) -> list:
        tab = self.tableaux.get(code_tab)
        if not tab:
            return []
        sortie = []
        for r in tab["definition"]["ratios"]:
            num = self.evaluer_expression(r["numerateur"], code_tab, "N")
            den = self.evaluer_expression(r["denominateur"], code_tab, "N")
            ligne = {
                "code": r["code"],
                "libelle": r["libelle"],
                "numerateur": str(num.quantize(Decimal("1"), ROUND_HALF_UP)),
                "denominateur": str(den.quantize(Decimal("1"), ROUND_HALF_UP)),
                "unite": r["unite"],
            }
            if den == 0:
                ligne.update({"valeur": None, "norme": "Non calculable (denominateur nul)", "ecart": None, "conforme": None})
            else:
                val = num / den
                if r["unite"] == "POURCENTAGE":
                    val *= 100
                val = val.quantize(Decimal("0.01"), ROUND_HALF_UP)
                ligne["valeur"] = str(val)
                ligne.update(self.verifier_norme(val, r.get("normes", [])))
            sortie.append(ligne)
        return sortie

    def executer_audit_complet(self) -> dict:
        def arrondi(v):
            return v.quantize(Decimal("1"), ROUND_HALF_UP)

        actif = self.get_poste("DIMF2000_BILAN_DEV", "E90", "NET")
        passif = self.get_poste("DIMF2000_BILAN_DEV", "L90", "NET")
        charges = self.get_poste("DIMF2080_RESULTAT_DEV", "T84", "N")
        produits = self.get_poste("DIMF2080_RESULTAT_DEV", "X84", "N")
        res_bilan = self.get_poste("DIMF2000_BILAN_DEV", "L80", "NET")
        res_cr = self.get_poste("DIMF2080_RESULTAT_DEV", "L80", "N")
        tolerance = Decimal("1")

        fp = {
            "FP_ELEMENTS": self.get_poste("FONDS_PROPRES", "FP_ELEMENTS", "N"),
            "FP_DEDUCTIONS": self.get_poste("FONDS_PROPRES", "FP_DEDUCTIONS", "N"),
            "FP_NET": self.get_poste("FONDS_PROPRES", "FP", "N"),
        }
        ratios = {code: self._ratios(code) for code in ("RATIOS_PRUDENTIELS_010_016", "INDICATEURS_FINANCIERS_020")}

        return {
            "equilibres": {
                "bilan_actif_E90": str(arrondi(actif)),
                "bilan_passif_L90": str(arrondi(passif)),
                "bilan_equilibre": abs(actif - passif) <= tolerance,
                "resultat_bilan_L80": str(arrondi(res_bilan)),
                "resultat_cr_L80": str(arrondi(res_cr)),
                "coherence_resultat": abs(res_bilan - res_cr) <= tolerance,
                "total_charges_T84": str(arrondi(charges)),
                "total_produits_X84": str(arrondi(produits)),
                "charges_produits_equilibres": abs(charges - produits) <= tolerance,
            },
            "fonds_propres_prudentiels": {k: str(arrondi(v)) for k, v in fp.items()},
            "ratios": ratios,
            "grandeurs_manquantes": sorted(self.grandeurs_manquantes),
            "avertissements": sorted(self.avertissements),
        }


def main():
    parser = argparse.ArgumentParser(description="Audit des ratios BCEAO a partir d'une balance")
    parser.add_argument("balance", type=Path, help="balance CSV (compte;libelle;debit;credit)")
    parser.add_argument("grandeurs", type=Path, nargs="?", help="JSON des grandeurs saisies et du statut")
    parser.add_argument("--n1", type=Path, help="balance de l'exercice N-1 (pour MOYENNE)")
    parser.add_argument("--refs", type=Path, default=Path(__file__).resolve().parent.parent / "references")
    args = parser.parse_args()

    grandeurs, avertissements = {}, []
    statut = {"collecteDepots": True, "mutuelleAffiliee": False, "article44": False}
    if args.grandeurs:
        if not args.grandeurs.exists():
            sys.exit(f"Fichier introuvable : {args.grandeurs}")
        grandeurs, statut_lu, avertissements = charger_grandeurs(args.grandeurs)
        statut.update(statut_lu)

    moteur_n1 = None
    if args.n1:
        moteur_n1 = MoteurBCEAO(args.refs, charger_balance(args.n1), grandeurs, statut)
    moteur = MoteurBCEAO(args.refs, charger_balance(args.balance), grandeurs, statut, moteur_n1)

    rapport = moteur.executer_audit_complet()
    rapport["avertissements"] = sorted(set(rapport["avertissements"]) | set(avertissements))
    print(json.dumps(rapport, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()