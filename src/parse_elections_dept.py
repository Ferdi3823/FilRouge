"""
parse_elections_dept.py
=======================
Parse les fichiers XLS/XLSX des élections présidentielles françaises
(1995 → 2022) et produit deux CSV propres :

  outputs/elections_dept.csv     – résultats agrégés par département/tour
  outputs/elections_candidats.csv – voix par candidat/département/tour

Formats gérés
-------------
- 1995 / 2002 / 2007 / 2012 : feuille "Départements T1/T2"
    row 0 = en-têtes, row 1+ = données
    colonnes : Code, Libellé, Inscrits, Abstentions, …, puis blocs
    [Sexe | Nom | Prénom | Voix | %Ins | %Exp] répétés par candidat
- 2017 : feuille "Départements Tour 1/2"
    row 3 = en-têtes (3 lignes vides avant), même structure ensuite
- 2022 T1 (2022_01.xlsx) : niveau bureau de vote – on agrège par département
- 2022 T2 (2022_02.xlsx) : niveau commune – 2 candidats sur la même ligne,
    on agrège par département

Usage
-----
    python parse_elections_dept.py

Le script s'attend à être lancé depuis la racine du projet (FilRouge/).
Il peut aussi être lancé de n'importe où si BASE_DIR est ajusté.
"""

import re
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning)

# ── Chemins ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "elections"
OUT_DIR = BASE_DIR / "outputs"
OUT_DIR.mkdir(exist_ok=True)

# ── Helpers ────────────────────────────────────────────────────────────────────

def norm(s: str) -> str:
    """Normalise une chaîne : strip, lower, espaces simples."""
    return re.sub(r"\s+", " ", str(s).strip().lower())


def clean_num(x):
    """Convertit une valeur en float (gère ',' décimal et NaN)."""
    if pd.isna(x):
        return np.nan
    s = str(x).replace(",", ".").replace(" ", "").strip()
    try:
        return float(s)
    except ValueError:
        return np.nan


# ── Format A : 1995 / 2002 / 2007 / 2012 ──────────────────────────────────────

def parse_format_a(file: Path, year: int, tour: int) -> pd.DataFrame:
    """
    Feuilles "Départements T1/T2".
    Row 0 = en-têtes, row 1+ = données.
    Blocs candidats : [Sexe, Nom, Prénom, Voix, %Ins, %Exp] × N
    """
    sheet_map = {1: f"Départements T{tour}", 2: f"Départements T{tour}"}
    sheet_name = sheet_map[tour]

    engine = "xlrd" if file.suffix == ".xls" else "openpyxl"
    df_raw = pd.read_excel(file, sheet_name=sheet_name, header=None, engine=engine)

    # L'en-tête est en ligne 0
    headers = [norm(c) for c in df_raw.iloc[0]]
    data = df_raw.iloc[1:].copy()
    data.columns = headers
    data = data.dropna(subset=["code du département"]).copy()
    data = data[data["code du département"].astype(str).str.strip() != ""].copy()

    rows = []
    for _, row in data.iterrows():
        dept_code = str(row["code du département"]).strip().zfill(2)
        dept_nom = str(row.get("libellé du département", "")).strip()
        inscrits = clean_num(row.get("inscrits"))
        votants = clean_num(row.get("votants"))
        exprimes = clean_num(row.get("exprimés"))
        abstentions = clean_num(row.get("abstentions"))

        # Récupérer les blocs candidats
        # Chercher toutes les positions "sexe" dans les colonnes
        cols = list(data.columns)
        sexe_positions = [i for i, c in enumerate(cols) if c == "sexe"]

        candidats = []
        for pos in sexe_positions:
            try:
                nom_val = str(row.iloc[pos + 1]).strip()
                prenom_val = str(row.iloc[pos + 2]).strip()
                voix_val = clean_num(row.iloc[pos + 3])
                if pd.isna(voix_val) or nom_val in ("nan", ""):
                    continue
                # Nom complet : on concatène Nom + Prénom
                nom_complet = f"{nom_val} {prenom_val}".strip()
                candidats.append({"candidat": nom_complet, "voix": voix_val})
            except IndexError:
                continue

        rows.append({
            "annee": year,
            "tour": tour,
            "dept_code": dept_code,
            "dept_nom": dept_nom,
            "inscrits": inscrits,
            "votants": votants,
            "abstentions": abstentions,
            "exprimes": exprimes,
            "candidats": candidats,
        })

    return rows


# ── Format B : 2017 ─────────────────────────────────────────────────────────────

def parse_format_b_2017(file: Path, tour: int) -> list:
    """
    Feuille "Départements Tour 1/2".
    3 lignes vides + 1 ligne d'en-tête (row 3), données à partir de row 4.
    2017 distingue Blancs / Nuls séparément.
    """
    sheet_name = f"Départements Tour {tour}"
    engine = "xlrd"
    df_raw = pd.read_excel(file, sheet_name=sheet_name, header=None, engine=engine)

    # Ligne d'en-tête : row 3
    headers = [norm(c) for c in df_raw.iloc[3]]
    data = df_raw.iloc[4:].copy()
    data.columns = headers
    data = data.dropna(subset=["code du département"]).copy()
    # Filtrer les lignes vides / totaux
    data = data[pd.to_numeric(data["code du département"], errors="coerce").notna()].copy()

    rows = []
    cols = list(data.columns)
    sexe_positions = [i for i, c in enumerate(cols) if c == "sexe"]

    for _, row in data.iterrows():
        dept_code = str(int(clean_num(row["code du département"]))).zfill(2)
        dept_nom = str(row.get("libellé du département", "")).strip()
        inscrits = clean_num(row.get("inscrits"))
        votants = clean_num(row.get("votants"))
        exprimes = clean_num(row.get("exprimés"))
        abstentions = clean_num(row.get("abstentions"))

        candidats = []
        for pos in sexe_positions:
            try:
                nom_val = str(row.iloc[pos + 1]).strip()
                prenom_val = str(row.iloc[pos + 2]).strip()
                voix_val = clean_num(row.iloc[pos + 3])
                if pd.isna(voix_val) or nom_val in ("nan", ""):
                    continue
                nom_complet = f"{nom_val} {prenom_val}".strip()
                candidats.append({"candidat": nom_complet, "voix": voix_val})
            except IndexError:
                continue

        rows.append({
            "annee": 2017,
            "tour": tour,
            "dept_code": dept_code,
            "dept_nom": dept_nom,
            "inscrits": inscrits,
            "votants": votants,
            "abstentions": abstentions,
            "exprimes": exprimes,
            "candidats": candidats,
        })

    return rows


# ── Format C : 2022 T1 (niveau bureau de vote) ──────────────────────────────────

def parse_2022_t1(file: Path) -> list:
    """
    2022_01.xlsx : niveau bureau de vote.
    On agrège par département.
    Candidats sur la même ligne, blocs répétés [N°Panneau, Sexe, Nom, Prénom,
    Voix, %Voix/Ins, %Voix/Exp] après Exprimés. Excel ne répète le texte de
    l'en-tête que pour le 1er candidat ; pandas renomme les colonnes vides en
    "Unnamed: N", donc on repère les blocs par position (stride de 7) plutôt
    que par le nom de colonne "sexe", qui ne matcherait que le 1er candidat.
    """
    df_raw = pd.read_excel(file, sheet_name=0, header=0, engine="openpyxl")
    norm_cols = [norm(c) for c in df_raw.columns]

    dept_col_idx = norm_cols.index("code du département")
    dept_nom_col_idx = norm_cols.index("libellé du département")
    inscrits_idx = norm_cols.index("inscrits")
    votants_idx = norm_cols.index("votants")
    abstentions_idx = norm_cols.index("abstentions")
    exprimes_idx = norm_cols.index("exprimés")

    # 1er bloc candidat : repéré par la colonne "N°Panneau", puis stride de 7
    block_start = next(i for i, c in enumerate(norm_cols) if "panneau" in c)
    block_starts = list(range(block_start, len(norm_cols), 7))

    # Agrégat inscrits/votants/abstentions/exprimes : une ligne par bureau de
    # vote, calculé AVANT l'explosion par candidat (sinon ces valeurs seraient
    # comptées une fois par candidat lors du groupby plus bas).
    base = pd.DataFrame({
        "dept_code": df_raw.iloc[:, dept_col_idx].astype(str).str.strip().str.zfill(2),
        "dept_nom": df_raw.iloc[:, dept_nom_col_idx].astype(str).str.strip(),
        "inscrits": df_raw.iloc[:, inscrits_idx].apply(clean_num),
        "votants": df_raw.iloc[:, votants_idx].apply(clean_num),
        "abstentions": df_raw.iloc[:, abstentions_idx].apply(clean_num),
        "exprimes": df_raw.iloc[:, exprimes_idx].apply(clean_num),
    })
    dept_agg = (
        base.groupby(["dept_code", "dept_nom"])
        .agg(inscrits=("inscrits", "sum"), votants=("votants", "sum"),
             abstentions=("abstentions", "sum"), exprimes=("exprimes", "sum"))
        .reset_index()
    )

    # Construire un df candidats long (uniquement dept_code/candidat/voix)
    records = []
    for _, row in df_raw.iterrows():
        dept_code = str(row.iloc[dept_col_idx]).strip().zfill(2)
        for pos in block_starts:
            try:
                nom_val = str(row.iloc[pos + 2]).strip()
                prenom_val = str(row.iloc[pos + 3]).strip()
                voix_val = clean_num(row.iloc[pos + 4])
                if pd.isna(voix_val) or nom_val in ("nan", ""):
                    continue
                nom_complet = f"{nom_val} {prenom_val}".strip()
                records.append({
                    "dept_code": dept_code,
                    "candidat": nom_complet,
                    "voix": voix_val,
                })
            except IndexError:
                continue

    long_df = pd.DataFrame(records)
    cand_agg = (
        long_df.groupby(["dept_code", "candidat"])["voix"]
        .sum()
        .reset_index()
    )

    rows = []
    for _, d in dept_agg.iterrows():
        cands = cand_agg[cand_agg["dept_code"] == d["dept_code"]]
        candidats = [{"candidat": r["candidat"], "voix": r["voix"]}
                     for _, r in cands.iterrows()]
        rows.append({
            "annee": 2022, "tour": 1,
            "dept_code": d["dept_code"], "dept_nom": d["dept_nom"],
            "inscrits": d["inscrits"], "votants": d["votants"],
            "abstentions": d["abstentions"], "exprimes": d["exprimes"],
            "candidats": candidats,
        })
    return rows


# ── Format D : 2022 T2 (niveau commune, 2 candidats) ───────────────────────────

def parse_2022_t2(file: Path) -> list:
    """
    2022_02.xlsx : niveau commune, 2 candidats côte à côte sur la même ligne.
    Colonnes candidat 1 : Sexe(20) Nom(21) Prénom(22) Voix(23) …
    Colonnes candidat 2 : col 26(N°Panneau) Sexe(27→col?) — on repère par 'unnamed'
    """
    df = pd.read_excel(file, sheet_name=0, header=0, engine="openpyxl")
    # Renommer les colonnes unnamed avec un suffixe numérique
    cols = []
    unnamed_count = 0
    for c in df.columns:
        if str(c).startswith("Unnamed"):
            cols.append(f"_c{unnamed_count}")
            unnamed_count += 1
        else:
            cols.append(c)
    df.columns = cols

    dept_col = "Code du département"
    dept_nom_col = "Libellé du département"

    # Candidat 1 : cols Sexe, Nom, Prénom, Voix (positions 20-23)
    # Candidat 2 : cols _c0=N°Panneau, _c1=Sexe, _c2=Nom, _c3=Prénom, _c4=Voix
    cand_blocks = [
        ("Sexe", "Nom", "Prénom", "Voix"),
        ("_c1", "_c2", "_c3", "_c4"),
    ]

    # Agrégat inscrits/votants/abstentions/exprimes : une ligne par commune,
    # calculé AVANT l'explosion par candidat (sinon ces valeurs sont comptées
    # deux fois lors du groupby plus bas, une fois par candidat).
    base = df.copy()
    base["dept_code"] = base[dept_col].astype(str).str.strip().str.zfill(2)
    base["dept_nom"] = base[dept_nom_col].astype(str).str.strip()
    base["inscrits"] = base.get("Inscrits").apply(clean_num)
    base["votants"] = base.get("Votants").apply(clean_num)
    base["abstentions"] = base.get("Abstentions").apply(clean_num)
    base["exprimes"] = base.get("Exprimés").apply(clean_num)
    dept_agg = (
        base.groupby(["dept_code", "dept_nom"])
        .agg(inscrits=("inscrits", "sum"), votants=("votants", "sum"),
             abstentions=("abstentions", "sum"), exprimes=("exprimes", "sum"))
        .reset_index()
    )

    records = []
    for _, row in df.iterrows():
        dept_code = str(row[dept_col]).strip().zfill(2)

        for sexe_col, nom_col, prenom_col, voix_col in cand_blocks:
            nom_val = str(row.get(nom_col, "")).strip()
            prenom_val = str(row.get(prenom_col, "")).strip()
            voix_val = clean_num(row.get(voix_col))
            if pd.isna(voix_val) or nom_val in ("nan", ""):
                continue
            nom_complet = f"{nom_val} {prenom_val}".strip()
            records.append({
                "dept_code": dept_code,
                "candidat": nom_complet, "voix": voix_val,
            })

    long_df = pd.DataFrame(records)
    cand_agg = (
        long_df.groupby(["dept_code", "candidat"])["voix"]
        .sum()
        .reset_index()
    )

    rows = []
    for _, d in dept_agg.iterrows():
        cands = cand_agg[cand_agg["dept_code"] == d["dept_code"]]
        candidats = [{"candidat": r["candidat"], "voix": r["voix"]}
                     for _, r in cands.iterrows()]
        rows.append({
            "annee": 2022, "tour": 2,
            "dept_code": d["dept_code"], "dept_nom": d["dept_nom"],
            "inscrits": d["inscrits"], "votants": d["votants"],
            "abstentions": d["abstentions"], "exprimes": d["exprimes"],
            "candidats": candidats,
        })
    return rows


# ── Pipeline principal ──────────────────────────────────────────────────────────

def main():
    all_rows = []

    tasks = [
        # (fichier, année, tour, format)
        ("1995_t1.xls", 1995, 1, "A"),
        ("1995_t2.xls", 1995, 2, "A"),
        ("2002_t1.xls", 2002, 1, "A"),
        ("2002_t2.xls", 2002, 2, "A"),
        ("2007_t1.xls", 2007, 1, "A"),
        ("2007_t2.xls", 2007, 2, "A"),
        ("2012_t1.xls", 2012, 1, "A"),
        ("2012_t2.xls", 2012, 2, "A"),
        ("2017_01.xls", 2017, 1, "B"),
        ("2017_02.xls", 2017, 2, "B"),
        ("2022_01.xlsx", 2022, 1, "C"),
        ("2022_02.xlsx", 2022, 2, "D"),
    ]

    for fname, year, tour, fmt in tasks:
        fpath = DATA_DIR / fname
        if not fpath.exists():
            print(f"  ⚠️  Fichier manquant : {fname}")
            continue
        print(f"  📂 {fname} …", end=" ")
        try:
            if fmt == "A":
                rows = parse_format_a(fpath, year, tour)
            elif fmt == "B":
                rows = parse_format_b_2017(fpath, tour)
            elif fmt == "C":
                rows = parse_2022_t1(fpath)
            elif fmt == "D":
                rows = parse_2022_t2(fpath)
            else:
                rows = []
            all_rows.extend(rows)
            print(f"✅  {len(rows)} départements")
        except Exception as e:
            print(f"❌  ERREUR : {e}")

    if not all_rows:
        print("\n❌ Aucune donnée chargée.")
        return

    # ── CSV 1 : résumé par département ────────────────────────────────────────
    summary_rows = []
    for r in all_rows:
        summary_rows.append({
            "annee": r["annee"],
            "tour": r["tour"],
            "dept_code": r["dept_code"],
            "dept_nom": r["dept_nom"],
            "inscrits": r["inscrits"],
            "votants": r["votants"],
            "abstentions": r["abstentions"],
            "exprimes": r["exprimes"],
        })
    df_summary = pd.DataFrame(summary_rows)
    df_summary = df_summary.drop_duplicates(subset=["annee", "tour", "dept_code"])
    df_summary = df_summary.sort_values(["annee", "tour", "dept_code"])
    out1 = OUT_DIR / "elections_dept.csv"
    df_summary.to_csv(out1, index=False, encoding="utf-8-sig")
    print(f"\n✅ {out1.name} — {len(df_summary)} lignes")

    # ── CSV 2 : voix par candidat ──────────────────────────────────────────────
    cand_rows = []
    for r in all_rows:
        for c in r["candidats"]:
            cand_rows.append({
                "annee": r["annee"],
                "tour": r["tour"],
                "dept_code": r["dept_code"],
                "dept_nom": r["dept_nom"],
                "candidat": c["candidat"],
                "voix": c["voix"],
            })
    df_cand = pd.DataFrame(cand_rows)
    # Calculer le % des exprimés en joignant le summary
    df_cand = df_cand.merge(
        df_summary[["annee", "tour", "dept_code", "exprimes"]],
        on=["annee", "tour", "dept_code"], how="left"
    )
    df_cand["pct_exprimes"] = (df_cand["voix"] / df_cand["exprimes"] * 100).round(2)
    df_cand = df_cand.sort_values(["annee", "tour", "dept_code", "voix"], ascending=[True, True, True, False])
    out2 = OUT_DIR / "elections_candidats.csv"
    df_cand.to_csv(out2, index=False, encoding="utf-8-sig")
    print(f"✅ {out2.name} — {len(df_cand)} lignes")

    # ── Aperçu qualité ────────────────────────────────────────────────────────
    print("\n── Aperçu qualité ──────────────────────────────────────────────────")
    print(df_summary.groupby(["annee", "tour"])["dept_code"].count().to_string())
    print("\nCandidats 2022 T2 :")
    print(df_cand[(df_cand["annee"] == 2022) & (df_cand["tour"] == 2)]
          .groupby("candidat")["voix"].sum().to_string())
    print("\nTop candidats 2017 T1 (national) :")
    top17 = (df_cand[(df_cand["annee"] == 2017) & (df_cand["tour"] == 1)]
             .groupby("candidat")["voix"].sum()
             .sort_values(ascending=False).head(5))
    print(top17.to_string())
    print("\n🎉 Parsing terminé.")


if __name__ == "__main__":
    print("═" * 60)
    print("  Parser élections présidentielles françaises 1995–2022")
    print("═" * 60)
    main()
