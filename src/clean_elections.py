import pandas as pd
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "elections"
OUTPUT_PATH = BASE_DIR / "outputs"
OUTPUT_PATH.mkdir(exist_ok=True)

files = list(DATA_PATH.glob("*.xls")) + list(DATA_PATH.glob("*.xlsx"))

def parse_year_tour(filename: str):
    name = filename.lower()

    if "95" in name or "1995" in name:
        year = 1995
    elif "02" in name or "2002" in name:
        year = 2002
    elif "07" in name or "2007" in name:
        year = 2007
    elif "12" in name or "2012" in name:
        year = 2012
    elif "2017" in name or "17" in name:
        year = 2017
    elif "2022" in name or "22" in name:
        year = 2022
    else:
        year = None

    if "t1" in name or "01" in name:
        tour = 1
    elif "t2" in name or "02" in name or "2t" in name:
        tour = 2
    else:
        tour = None

    return year, tour

def normalize_columns(df: pd.DataFrame):
    df = df.copy()
    df.columns = [
        str(c).strip().lower().replace("\n", " ").replace("\r", " ")
        for c in df.columns
    ]
    return df

all_frames = []

for file in files:
    print(f"\nLecture : {file.name}")
    try:
        df = pd.read_excel(file)
        df = normalize_columns(df)

        year, tour = parse_year_tour(file.name)
        df["annee"] = year
        df["tour"] = tour
        df["source_file"] = file.name

        all_frames.append(df)
        print("OK - shape :", df.shape)
    except Exception as e:
        print("Erreur :", e)

if not all_frames:
    raise ValueError("Aucun fichier chargé.")

raw = pd.concat(all_frames, ignore_index=True)
raw.to_csv(OUTPUT_PATH / "all_elections_raw_normalized.csv", index=False)

print("\nFichier généré :", OUTPUT_PATH / "all_elections_raw_normalized.csv")
print("Nombre total de lignes :", len(raw))
print("Nombre total de colonnes :", len(raw.columns))