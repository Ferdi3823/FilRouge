import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "elections"

files = list(DATA_PATH.glob("*.xls")) + list(DATA_PATH.glob("*.xlsx"))

for file in files:
    print("\n" + "=" * 80)
    print("FICHIER :", file.name)
    try:
        df = pd.read_excel(file)
        print("Shape :", df.shape)
        print("Colonnes :")
        for col in df.columns:
            print("-", repr(col))
        print("\nAperçu :")
        print(df.head(3).to_string())
    except Exception as e:
        print("Erreur :", e)