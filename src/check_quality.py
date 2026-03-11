import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = BASE_DIR / "outputs"

df = pd.read_csv(OUTPUT_PATH / "all_elections_raw_normalized.csv")

print("Shape :", df.shape)
print("\nColonnes :")
print(df.columns.tolist())

print("\nValeurs manquantes par colonne :")
print(df.isna().sum().sort_values(ascending=False).head(30))

print("\nNombre de doublons :", df.duplicated().sum())
print("\nAnnées présentes :", sorted(df["annee"].dropna().unique().tolist()))
print("Tours présents :", sorted(df["tour"].dropna().unique().tolist()))