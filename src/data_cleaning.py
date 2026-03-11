import pandas as pd
from pathlib import Path

# chemin du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# chemin des fichiers élections
DATA_PATH = BASE_DIR / "data" / "elections"

print("Chemin projet :", BASE_DIR)
print("Chemin données :", DATA_PATH)

# récupérer fichiers
files = list(DATA_PATH.glob("*.xls")) + list(DATA_PATH.glob("*.xlsx"))

print("\nFichiers trouvés :")
for f in files:
    print(f.name)

all_data = []

for file in files:
    
    print("\nLecture :", file.name)
    
    try:
        df = pd.read_excel(file)
        
        df["source_file"] = file.name
        
        print("Nombre de lignes :", len(df))
        
        all_data.append(df)
        
    except Exception as e:
        print("Erreur lecture :", file.name)
        print(e)

# vérifier qu'on a des données
if len(all_data) == 0:
    print("\n❌ Aucun fichier n'a été chargé")
    exit()

# concaténer
data = pd.concat(all_data, ignore_index=True)

print("\nNombre total lignes :", len(data))

# sauvegarde
output_path = BASE_DIR / "outputs" / "raw_dataset.csv"

data.to_csv(output_path, index=False)

print("\nDataset brut sauvegardé dans outputs/")