"""
parse_legislatives.py
=====================
Parse les données d'abstention des législatives 2017 et 2022
par département, et les fusionne avec les données démographiques
pour enrichir le dataset de régression.

Sources
-------
  data/legislatives/leg2022_t{1,2}_dept.txt  — CSV ; latin-1, data.gouv.fr
  data/legislatives/leg2017_t{1,2}.xlsx      — feuille "Departements T1/T2"

Sortie
------
  outputs/tables/legislatives_dept.csv
  outputs/tables/regression_dataset_extended.csv   (présidentielles + légis)

Usage
-----
    python -X utf8 src/parse_legislatives.py
"""

import warnings
import numpy as np
import pandas as pd
from pathlib import Path

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent
LEG_DIR  = BASE_DIR / "data" / "legislatives"
OUT_DIR  = BASE_DIR / "outputs"
TBL_DIR  = OUT_DIR  / "tables"
TBL_DIR.mkdir(parents=True, exist_ok=True)

DEMO_FILE = OUT_DIR / "elections_with_demography.csv"

DOM_CODES = {"971", "972", "973", "974", "975", "976"}

# Colonnes finales exportées
COLS_OUT = ["annee", "tour", "type_election", "dept_code",
            "inscrits", "abstentions", "taux_abstention"]


# ── Normalisation code département ─────────────────────────────────────────────

def normalize_dept_code(raw) -> str:
    """'1' → '01', '2A' → '2A', '971' → '971', etc."""
    s = str(raw).strip().upper()
    if s in ("2A", "2B"):
        return s
    try:
        n = int(float(s))
        if n < 10:
            return f"0{n}"
        return str(n)
    except (ValueError, OverflowError):
        return s


# ── Parseur 2022 TXT ───────────────────────────────────────────────────────────

def parse_leg2022_txt(filepath, tour: int) -> pd.DataFrame:
    """
    Les fichiers TXT 2022 ont un header de 22 champs puis des lignes
    de 77–87 champs (colonnes candidats variables). On garde les 22 premiers.
    """
    with open(filepath, encoding="latin-1") as f:
        lines = f.readlines()

    header = lines[0].strip().split(";")
    n_header = len(header)

    rows = []
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split(";")
        rows.append(parts[:n_header])

    df = pd.DataFrame(rows, columns=header)

    rename = {
        "Code du département": "dept_code_raw",
        "Inscrits":            "inscrits",
        "Abstentions":         "abstentions",
        "% Abs/Ins":           "taux_abstention",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    for col in ["inscrits", "abstentions"]:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(" ", "").str.replace("\xa0", ""),
            errors="coerce"
        )
    df["taux_abstention"] = (
        df["taux_abstention"].astype(str).str.replace(",", ".").pipe(pd.to_numeric, errors="coerce")
    )

    df["dept_code"] = df["dept_code_raw"].apply(normalize_dept_code)
    df["annee"] = 2022
    df["tour"] = tour
    df["type_election"] = "legislatives"

    # Filtre : DOM + lignes sans données valides
    df = df[~df["dept_code"].isin(DOM_CODES)]
    df = df.dropna(subset=["inscrits", "taux_abstention"])
    df = df[df["inscrits"] > 0]

    return df[COLS_OUT]


# ── Parseur 2017 XLSX ──────────────────────────────────────────────────────────

def parse_leg2017_xlsx(filepath, tour: int) -> pd.DataFrame:
    """
    Feuille 'Departements T{tour}' : 2 lignes titre/vide + ligne header + données.
    skiprows=[0,1] → row 2 becomes header=0.
    """
    sheet = f"Departements T{tour}"
    df = pd.read_excel(filepath, sheet_name=sheet, skiprows=[0, 1], header=0)

    rename = {
        "Code du département":   "dept_code_raw",
        "Inscrits":              "inscrits",
        "Abstentions":           "abstentions",
        "% Abs/Ins":             "taux_abstention",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    for col in ["inscrits", "abstentions"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["taux_abstention"] = pd.to_numeric(df["taux_abstention"], errors="coerce")

    df["dept_code"] = df["dept_code_raw"].apply(normalize_dept_code)
    df["annee"] = 2017
    df["tour"] = tour
    df["type_election"] = "legislatives"

    df = df[~df["dept_code"].isin(DOM_CODES)]
    df = df.dropna(subset=["inscrits", "taux_abstention"])
    df = df[df["inscrits"] > 0]

    return df[COLS_OUT]


# ── Fusion avec données démographiques ────────────────────────────────────────

def merge_with_demography(df_leg: pd.DataFrame, df_demo: pd.DataFrame) -> pd.DataFrame:
    """
    Joint les données légis avec la démographie de la même année.

    La démographie disponible dans df_demo correspond aux années électorales
    présidentielles (1995, 2002, 2007, 2012, 2017, 2022). Les législatives
    ayant lieu la même année, on utilise les données INSEE de l'année présidentielle
    correspondante (même millésime).

    Colonnes ajoutées : pct_jeunes, pct_actifs, pct_seniors, ratio_seniors_jeunes,
                        pop_ens_total, is_legislatives (=1)
    """
    demo_cols = [
        "annee", "dept_code", "tour",
        "pct_jeunes", "pct_actifs", "pct_seniors", "ratio_seniors_jeunes",
        "pop_ens_total",
    ]
    demo_t1 = (
        df_demo[df_demo["tour"] == 1][demo_cols]
        .rename(columns={"tour": "tour_demo"})
    )

    # Join sur (annee, dept_code) — la démographie ne dépend pas du tour
    merged = df_leg.merge(
        demo_t1.drop(columns="tour_demo"),
        on=["annee", "dept_code"],
        how="inner",
    )
    merged["is_legislatives"] = 1
    return merged


# ── Pipeline principal ────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Parse législatives 2017 & 2022")
    print("=" * 60)

    frames = []

    # 2022 TXT
    for tour in [1, 2]:
        fp = LEG_DIR / f"leg2022_t{tour}_dept.txt"
        if not fp.exists():
            print(f"  [WARN] Fichier manquant : {fp.name}")
            continue
        df = parse_leg2022_txt(fp, tour)
        frames.append(df)
        natl = (df["abstentions"].sum() / df["inscrits"].sum() * 100)
        print(f"  2022 T{tour} — {len(df)} depts, abstention nationale : {natl:.1f}%")

    # 2017 XLSX
    for tour in [1, 2]:
        fp = LEG_DIR / f"leg2017_t{tour}.xlsx"
        if not fp.exists():
            print(f"  [WARN] Fichier manquant : {fp.name}")
            continue
        df = parse_leg2017_xlsx(fp, tour)
        frames.append(df)
        natl = (df["abstentions"].sum() / df["inscrits"].sum() * 100)
        print(f"  2017 T{tour} — {len(df)} depts, abstention nationale : {natl:.1f}%")

    if not frames:
        print("Aucun fichier trouvé — arrêt.")
        return

    df_leg = pd.concat(frames, ignore_index=True)
    out_path = TBL_DIR / "legislatives_dept.csv"
    df_leg.to_csv(out_path, index=False)
    print(f"\n  Sauvegardé : {out_path.name}  ({len(df_leg)} lignes)")

    # Fusion avec démographie pour dataset étendu
    if not DEMO_FILE.exists():
        print("  [WARN] elections_with_demography.csv introuvable — fusion ignorée.")
        return

    df_demo = pd.read_csv(DEMO_FILE)
    print(f"\nChargé : {DEMO_FILE.name}  {df_demo.shape}")

    df_merged = merge_with_demography(df_leg, df_demo)
    print(f"Fusion réussie : {len(df_merged)} lignes (sur {len(df_leg)} législatives)")

    # Dataset étendu = présidentielles T1 + législatives T1
    pres_cols = [
        "annee", "dept_code", "tour", "inscrits", "abstentions",
        "taux_abstention", "pct_jeunes", "pct_actifs", "pct_seniors",
        "ratio_seniors_jeunes", "pop_ens_total",
    ]
    pres_t1 = df_demo[df_demo["tour"] == 1][pres_cols].copy()
    pres_t1["is_legislatives"] = 0
    pres_t1["type_election"] = "presidentielles"

    leg_t1 = df_merged[df_merged["tour"] == 1].copy()
    leg_t1_cols = [c for c in pres_t1.columns if c in leg_t1.columns or c == "is_legislatives"]
    leg_t1 = leg_t1[leg_t1_cols]

    # Harmonise colonnes
    all_cols = [c for c in pres_t1.columns if c in leg_t1.columns]
    combined = pd.concat([pres_t1[all_cols], leg_t1[all_cols]], ignore_index=True)
    combined = combined.sort_values(["dept_code", "annee", "is_legislatives"]).reset_index(drop=True)

    ext_path = TBL_DIR / "regression_dataset_extended.csv"
    combined.to_csv(ext_path, index=False)
    print(f"  Dataset étendu sauvegardé : {ext_path.name}  ({len(combined)} lignes)")

    # Résumé
    summary = combined.groupby(["annee", "is_legislatives"]).agg(
        n_depts=("dept_code", "count"),
        abstention_moy=("taux_abstention", "mean"),
    ).round(1)
    print("\nRésumé par année × type :")
    print(summary.to_string())


if __name__ == "__main__":
    main()
