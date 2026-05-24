import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ELECTIONS_FILE = BASE_DIR / "outputs" / "elections_dept.csv"
POPULATION_FILE = BASE_DIR / "data" / "population" / "estim-pop-dep-sexe-gca-1975-2024.xls"
OUTPUT_DIR = BASE_DIR / "outputs"

ELECTION_YEARS = [1995, 2002, 2007, 2012, 2017, 2022]

# Groupes d'âge dans le fichier INSEE (Ensemble, Hommes, Femmes × 5 groupes + Total)
AGE_LABELS = ["0_19", "20_39", "40_59", "60_74", "75p", "total"]
SEXE_LABELS = ["ens", "h", "f"]

# Codes spéciaux dans les fichiers électoraux -> codes INSEE
OVERSEAS_MAP = {
    "ZA": "971",  # Guadeloupe
    "ZB": "972",  # Martinique
    "ZC": "973",  # Guyane
    "ZD": "974",  # La Réunion
    "ZM": "976",  # Mayotte
    "ZN": "987",  # Polynésie française
    "ZP": "975",  # Saint-Pierre-et-Miquelon
    "ZS": "977",  # Saint-Barthélemy / Saint-Martin
    "ZW": "986",  # Wallis-et-Futuna
    "ZZ": None,   # Français de l'étranger (pas de code INSEE géographique)
}


def normalize_dept_code(val):
    """Normalise un code département en chaîne à 2 caractères (ex. 1 -> '01', '2A' -> '2A')."""
    s = str(val).strip().upper()
    if s in OVERSEAS_MAP:
        return OVERSEAS_MAP[s] or s  # ZZ reste ZZ (pas de correspondance INSEE)
    if "." in s and s.replace(".", "").isdigit():
        s = str(int(float(s)))
    if s.isdigit():
        n = int(s)
        return s.zfill(2) if n <= 95 else s  # DOM : 971-976
    return s  # 2A, 2B, etc.


def load_population_year(xls_path, year):
    """Charge les données de population par groupe d'âge et département pour une année."""
    xl = pd.ExcelFile(xls_path, engine="xlrd")

    sheet = str(year)
    if sheet not in xl.sheet_names:
        candidates = [s for s in xl.sheet_names if str(year) in s]
        if not candidates:
            raise ValueError(f"Onglet '{year}' introuvable. Disponibles : {xl.sheet_names[:8]}")
        sheet = candidates[0]

    raw = pd.read_excel(xls_path, sheet_name=sheet, header=None, engine="xlrd")

    # Détection de la première ligne de données (code dept numérique 1–10)
    data_start = 4  # valeur par défaut
    for i, row in raw.iterrows():
        val = str(row.iloc[0]).strip().replace(".0", "")
        if val.isdigit() and 1 <= int(val) <= 10:
            data_start = i
            break

    df = raw.iloc[data_start:].reset_index(drop=True)

    # Nommage des colonnes : code, nom, puis groupes d'âge pour ens/h/f
    col_names = ["dept_code", "dept_nom"]
    for sexe in SEXE_LABELS:
        for age in AGE_LABELS:
            col_names.append(f"pop_{sexe}_{age}")

    n = min(len(col_names), df.shape[1])
    df = df.iloc[:, :n]
    df.columns = col_names[:n]

    # Normalisation et filtrage des codes département valides
    df["dept_code"] = df["dept_code"].apply(normalize_dept_code)
    valid = r"^(0[1-9]|[1-8]\d|9[0-5]|2[AB]|97[1-6])$"
    df = df[df["dept_code"].str.match(valid, na=False)].copy()

    # Conversion numérique
    for col in col_names[2:n]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["annee_pop"] = year

    keep = ["dept_code", "dept_nom", "annee_pop"]
    keep += [f"pop_ens_{a}" for a in AGE_LABELS if f"pop_ens_{a}" in df.columns]

    return df[keep].reset_index(drop=True)


def compute_derived_features(df):
    """Calcule les indicateurs démographiques et électoraux."""
    pop = df["pop_ens_total"].replace(0, np.nan)

    # Pyramide d'âge (%)
    jeunes = df.get("pop_ens_0_19", 0) + df.get("pop_ens_20_39", 0)
    actifs = df.get("pop_ens_40_59", 0)
    seniors = df.get("pop_ens_60_74", 0) + df.get("pop_ens_75p", 0)

    df["pct_jeunes"] = (jeunes / pop * 100).round(2)
    df["pct_actifs"] = (actifs / pop * 100).round(2)
    df["pct_seniors"] = (seniors / pop * 100).round(2)
    df["ratio_seniors_jeunes"] = (seniors / jeunes.replace(0, np.nan)).round(3)

    # Taux électoraux (%)
    df["taux_participation"] = (df["votants"] / df["inscrits"] * 100).round(2)
    df["taux_abstention"] = (df["abstentions"] / df["inscrits"] * 100).round(2)

    return df


def main():
    print("=== Fusion élections + démographie INSEE ===\n")

    elections = pd.read_csv(ELECTIONS_FILE)
    elections["dept_code"] = elections["dept_code"].apply(normalize_dept_code)
    print(f"Élections : {elections.shape[0]} lignes | années {sorted(elections['annee'].unique())}")

    # Chargement de la population par année électorale
    pop_frames = []
    for year in ELECTION_YEARS:
        try:
            df_pop = load_population_year(POPULATION_FILE, year)
            pop_frames.append(df_pop)
            print(f"  Population {year} : {len(df_pop)} départements")
        except Exception as e:
            print(f"  [WARN] {year} : {e}")

    if not pop_frames:
        raise RuntimeError("Aucune donnée démographique n'a pu être chargée.")

    pop_all = pd.concat(pop_frames, ignore_index=True)

    # Fusion sur dept_code + annee
    # Renommage pour éviter le doublon dept_nom_x / dept_nom_y
    elections = elections.rename(columns={"dept_nom": "dept_nom_election"})

    merged = elections.merge(
        pop_all,
        left_on=["dept_code", "annee"],
        right_on=["dept_code", "annee_pop"],
        how="left",
    )
    merged = merged.drop(columns=["annee_pop"], errors="ignore")

    # Diagnostic des valeurs manquantes
    missing = merged["pop_ens_total"].isna().sum()
    if missing:
        codes_manquants = merged[merged["pop_ens_total"].isna()]["dept_code"].unique()
        print(f"\n  [WARN] {missing} lignes sans données pop — codes : {list(codes_manquants[:10])}")
    else:
        print("\n  Fusion sans valeurs manquantes.")

    # Indicateurs dérivés
    merged = compute_derived_features(merged)

    output_path = OUTPUT_DIR / "elections_with_demography.csv"
    merged.to_csv(output_path, index=False)

    print(f"\nFichier sauvegardé : {output_path}")
    print(f"Shape : {merged.shape[0]} lignes × {merged.shape[1]} colonnes")
    print(f"\nColonnes : {merged.columns.tolist()}")
    print("\nAperçu (3 premières lignes) :")
    print(merged.head(3).to_string())
    print("\nStats descriptives démographiques :")
    cols_stats = ["pct_jeunes", "pct_actifs", "pct_seniors", "taux_participation", "taux_abstention"]
    print(merged[cols_stats].describe().round(2))


if __name__ == "__main__":
    main()
