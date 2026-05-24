import pandas as pd
from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "outputs" / "all_elections_raw_normalized.csv"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# colonnes finales attendues
TARGET_COLUMNS = [
    "annee",
    "tour",
    "source_file",
    "code_departement",
    "departement",
    "code_commune",
    "commune",
    "inscrits",
    "abstentions",
    "votants",
    "blancs",
    "nuls",
    "exprimes",
    "candidat",
    "voix",
    "pourcentage",
]

# dictionnaire : colonne finale -> noms possibles rencontrés
COLUMN_CANDIDATES = {
    "code_departement": [
        "code du departement",
        "code département",
        "code departement",
        "dep",
        "departement code",
        "code_dep",
    ],
    "departement": [
        "departement",
        "département",
        "libelle du departement",
        "libellé du département",
        "nom du departement",
    ],
    "code_commune": [
        "code de la commune",
        "code commune",
        "commune code",
        "codcom",
        "code_insee",
    ],
    "commune": [
        "commune",
        "libelle de la commune",
        "libellé de la commune",
        "nom commune",
        "libelle commune",
    ],
    "inscrits": [
        "inscrits",
        "i.",
        "i",
    ],
    "abstentions": [
        "abstentions",
        "a.",
        "a",
    ],
    "votants": [
        "votants",
        "v.",
        "v",
    ],
    "blancs": [
        "blancs",
        "blancs et nuls",
        "blancs/nuls",
        "b. et n.",
        "b.n.",
        "b et n",
    ],
    "nuls": [
        "nuls",
        "n.",
        "n",
    ],
    "exprimes": [
        "exprimes",
        "exprimés",
        "e.",
        "e",
    ],
    "candidat": [
        "nom",
        "nom candidat",
        "candidat",
        "prenom nom",
        "candidats",
    ],
    "voix": [
        "voix",
        "voix/ins",
        "nb voix",
    ],
    "pourcentage": [
        "% voix/exp",
        "% voix/ins",
        "pourcentage",
        "%",
        "% exprimés",
        "% exprimes",
    ],
}

def clean_text(value):
    if pd.isna(value):
        return value
    return str(value).strip()

def find_existing_column(df, candidates):
    existing = {col.lower().strip(): col for col in df.columns}
    for cand in candidates:
        key = cand.lower().strip()
        if key in existing:
            return existing[key]
    return None

def to_numeric(series):
    # remplace virgules et espaces pour faciliter la conversion
    return pd.to_numeric(
        series.astype(str)
        .str.replace("\u00a0", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False),
        errors="coerce"
    )

def harmonize_dataframe(df):
    df = df.copy()

    # nettoyage noms colonnes
    df.columns = [str(c).strip().lower() for c in df.columns]

    # dataframe de sortie
    out = pd.DataFrame(index=df.index)

    # colonnes déjà connues
    for base_col in ["annee", "tour", "source_file"]:
        if base_col in df.columns:
            out[base_col] = df[base_col]
        else:
            out[base_col] = np.nan

    # colonnes mappées
    mapping_report = {}

    for target_col, candidates in COLUMN_CANDIDATES.items():
        found = find_existing_column(df, candidates)
        mapping_report[target_col] = found

        if found is not None:
            out[target_col] = df[found]
        else:
            out[target_col] = np.nan

    # nettoyage texte
    text_cols = [
        "code_departement",
        "departement",
        "code_commune",
        "commune",
        "candidat",
        "source_file",
    ]
    for col in text_cols:
        if col in out.columns:
            out[col] = out[col].apply(clean_text)

    # conversion numérique
    numeric_cols = [
        "inscrits",
        "abstentions",
        "votants",
        "blancs",
        "nuls",
        "exprimes",
        "voix",
        "pourcentage",
    ]
    for col in numeric_cols:
        if col in out.columns:
            out[col] = to_numeric(out[col])

    # garantir toutes les colonnes finales
    for col in TARGET_COLUMNS:
        if col not in out.columns:
            out[col] = np.nan

    out = out[TARGET_COLUMNS]

    return out, mapping_report

def main():
    print(f"Lecture du fichier : {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE, low_memory=False)

    print("Shape source :", df.shape)
    print("Colonnes source :")
    print(df.columns.tolist())

    harmonized, mapping_report = harmonize_dataframe(df)

    print("\nMapping détecté :")
    for k, v in mapping_report.items():
        print(f"- {k} <- {v}")

    # sauvegarde dataset harmonisé
    output_file = OUTPUT_DIR / "elections_harmonized.csv"
    harmonized.to_csv(output_file, index=False)

    # sauvegarde rapport mapping
    mapping_df = pd.DataFrame(
        [{"target_column": k, "source_column_found": v} for k, v in mapping_report.items()]
    )
    mapping_df.to_csv(OUTPUT_DIR / "harmonization_mapping_report.csv", index=False)

    print("\nDataset harmonisé sauvegardé :", output_file)
    print("Shape harmonisée :", harmonized.shape)

    print("\nValeurs manquantes principales :")
    print(harmonized.isna().sum().sort_values(ascending=False))

if __name__ == "__main__":
    main()