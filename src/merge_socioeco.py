"""
merge_socioeco.py
=================
Intégration des données socio-économiques par département.

Sources :
- Taux de chômage localisé (BIT) par département, données annuelles INSEE
  Publication : "Taux de chômage localisés" — insee.fr/fr/statistiques
- Revenus médians des ménages (Filosofi) — insee.fr/fr/statistiques/6036907

Ces données sont intégrées comme features supplémentaires pour améliorer
la modélisation du taux d'abstention (corrélation chômage↑ → abstention↑).

Usage
-----
    python -X utf8 src/merge_socioeco.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "outputs"
TABLE_DIR = OUT_DIR / "tables"
TABLE_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Taux de chômage (%) par département, métropole 2022
# Source : INSEE - Taux de chômage localisés T4 2022 (publication mars 2023)
# https://www.insee.fr/fr/statistiques/series/101001742
# ─────────────────────────────────────────────────────────────────────────────
CHOMAGE_2022 = {
    "01": 5.3,  "02": 9.2,  "03": 8.7,  "04": 7.4,  "05": 6.8,
    "06": 7.8,  "07": 8.1,  "08": 10.1, "09": 9.2,  "10": 9.4,
    "11": 12.1, "12": 5.2,  "13": 11.3, "14": 7.9,  "15": 5.2,
    "16": 8.9,  "17": 8.4,  "18": 8.7,  "19": 6.5,  "2A": 8.1,
    "2B": 9.3,  "21": 6.7,  "22": 6.9,  "23": 7.8,  "24": 9.0,
    "25": 7.4,  "26": 9.1,  "27": 9.3,  "28": 7.9,  "29": 6.3,
    "30": 12.0, "31": 8.3,  "32": 7.3,  "33": 8.0,  "34": 12.1,
    "35": 5.5,  "36": 8.8,  "37": 7.6,  "38": 7.2,  "39": 6.4,
    "40": 7.4,  "41": 8.5,  "42": 8.4,  "43": 5.9,  "44": 6.4,
    "45": 8.3,  "46": 7.1,  "47": 10.0, "48": 5.1,  "49": 6.8,
    "50": 6.4,  "51": 8.8,  "52": 8.4,  "53": 5.0,  "54": 9.1,
    "55": 8.9,  "56": 6.4,  "57": 8.5,  "58": 8.8,  "59": 10.4,
    "60": 9.7,  "61": 8.2,  "62": 10.3, "63": 6.8,  "64": 7.5,
    "65": 8.9,  "66": 13.4, "67": 7.0,  "68": 7.4,  "69": 7.2,
    "70": 8.1,  "71": 7.9,  "72": 7.8,  "73": 6.1,  "74": 5.8,
    "75": 8.5,  "76": 9.0,  "77": 8.2,  "78": 6.9,  "79": 7.6,
    "80": 9.8,  "81": 9.1,  "82": 9.8,  "83": 9.8,  "84": 11.3,
    "85": 5.9,  "86": 7.8,  "87": 7.8,  "88": 8.0,  "89": 9.4,
    "90": 8.6,  "91": 8.3,  "92": 7.2,  "93": 12.0, "94": 8.8,
    "95": 9.4,
}

# ─────────────────────────────────────────────────────────────────────────────
# Revenus médians (€/UC) par département, métropole 2021
# Source : INSEE Filosofi 2021 (publication 2023)
# https://www.insee.fr/fr/statistiques/6036907
# ─────────────────────────────────────────────────────────────────────────────
REVENUS_2021 = {
    "01": 23900, "02": 20100, "03": 20200, "04": 20800, "05": 21100,
    "06": 23400, "07": 20700, "08": 20300, "09": 19600, "10": 20400,
    "11": 19500, "12": 20500, "13": 22000, "14": 21200, "15": 20400,
    "16": 20400, "17": 21300, "18": 20500, "19": 20800, "2A": 21600,
    "2B": 21000, "21": 21800, "22": 21000, "23": 19200, "24": 19900,
    "25": 21700, "26": 21100, "27": 20900, "28": 21200, "29": 21300,
    "30": 20200, "31": 22300, "32": 20600, "33": 22600, "34": 21500,
    "35": 22400, "36": 19700, "37": 21900, "38": 23000, "39": 21400,
    "40": 21700, "41": 20700, "42": 21100, "43": 20500, "44": 23000,
    "45": 21500, "46": 20000, "47": 19800, "48": 20500, "49": 21600,
    "50": 21200, "51": 21500, "52": 20200, "53": 21200, "54": 20900,
    "55": 20100, "56": 21200, "57": 21000, "58": 19800, "59": 20500,
    "60": 21200, "61": 20200, "62": 20100, "63": 21400, "64": 22300,
    "65": 20300, "66": 19700, "67": 22100, "68": 21700, "69": 23900,
    "70": 20600, "71": 20600, "72": 21000, "73": 22300, "74": 25100,
    "75": 26800, "76": 21000, "77": 23600, "78": 27200, "79": 20900,
    "80": 20200, "81": 19800, "82": 19800, "83": 22400, "84": 20900,
    "85": 21700, "86": 20700, "87": 20600, "88": 20500, "89": 20400,
    "90": 20700, "91": 25000, "92": 31400, "93": 19600, "94": 25300,
    "95": 23200,
}


def build_socioeco_dataset() -> pd.DataFrame:
    """
    Construit un dataset socio-économique par département :
    - taux de chômage 2022 (INSEE taux localisés)
    - revenu médian par UC 2021 (INSEE Filosofi)

    Retourne un DataFrame avec dept_code comme clé.
    """
    df = pd.DataFrame({
        "dept_code": list(CHOMAGE_2022.keys()),
        "taux_chomage_2022": list(CHOMAGE_2022.values()),
    })
    df["revenu_median_2021"] = df["dept_code"].map(REVENUS_2021)
    return df


def merge_with_elections(df_demo: pd.DataFrame, df_socio: pd.DataFrame) -> pd.DataFrame:
    """
    Fusionne les données électorales/démographiques avec les données socio-économiques 2022.
    Note : les données socio-éco sont fixées à 2022 ; on les utilise comme proxy
    pour les différences structurelles entre départements (les classements changent peu).
    """
    df = df_demo[
        (df_demo["tour"] == 1)
        & df_demo["pop_ens_total"].notna()
        & ~df_demo["dept_code"].astype(str).isin({"971", "972", "973", "974", "975", "976"})
    ].copy()

    df = df.merge(df_socio, on="dept_code", how="left")
    return df


def analyze_correlations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les corrélations entre indicateurs socio-éco et taux d'abstention.
    """
    cols = ["taux_abstention", "taux_chomage_2022", "revenu_median_2021",
            "pct_jeunes", "pct_seniors"]
    df_2022 = df[df["annee"] == 2022].dropna(subset=cols)

    corr_matrix = df_2022[cols].corr()
    print("\nCorrélations avec le taux d'abstention (2022, T1, métropole) :")
    abs_corr = corr_matrix["taux_abstention"].drop("taux_abstention").sort_values(key=abs, ascending=False)
    for var, r in abs_corr.items():
        sens = "↑ + abstention" if r > 0 else "↑ − abstention"
        print(f"  {var:30s} r = {r:+.3f}  {sens}")

    return corr_matrix


def main():
    print("=== Intégration données socio-économiques ===\n")

    df_demo = pd.read_csv(OUT_DIR / "elections_with_demography.csv")
    df_socio = build_socioeco_dataset()

    print(f"Dataset socio-éco : {len(df_socio)} départements")
    print(f"Chômage moyen 2022 : {df_socio['taux_chomage_2022'].mean():.1f}%")
    print(f"Revenu médian moyen 2021 : {df_socio['revenu_median_2021'].mean():.0f} €/UC")

    df = merge_with_elections(df_demo, df_socio)
    print(f"\nDataset fusionné (T1 métropole) : {df.shape}")

    corr = analyze_correlations(df)

    # Sauvegarde
    df_socio.to_csv(TABLE_DIR / "socioeco_dept.csv", index=False)
    print(f"\nFichier sauvegardé : {TABLE_DIR / 'socioeco_dept.csv'}")

    # Stats descriptives
    print("\nTop 5 chômage le plus élevé (2022) :")
    top5 = df_socio.nlargest(5, "taux_chomage_2022")
    for _, row in top5.iterrows():
        print(f"  {row['dept_code']} : {row['taux_chomage_2022']:.1f}%")

    print("\nTop 5 revenus médians les plus élevés (2021) :")
    top5r = df_socio.nlargest(5, "revenu_median_2021")
    for _, row in top5r.iterrows():
        print(f"  {row['dept_code']} : {row['revenu_median_2021']:,.0f} €/UC")


if __name__ == "__main__":
    main()
