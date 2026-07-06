# Élections présidentielles françaises — Analyse & Prédictions 2027

Projet fil rouge B3 YNOV — Data Storytelling & Machine Learning

---

## Objectif

Analyser les scrutins présidentiels français de **1995 à 2022** (6 élections, 96–100 départements, ~7 000 résultats candidats) pour :
- Identifier les tendances d'abstention et les recompositions politiques
- Mesurer l'influence de la démographie sur le comportement électoral
- Projeter l'abstention au premier tour 2027 via un modèle Ridge

---

## Démo rapide

```bash
pip install -r requirements.txt
python -X utf8 src/merge_demography.py   # Step 1 : fusion élections + INSEE
python -X utf8 src/eda_analysis.py       # Step 2 : 10 figures EDA
python -X utf8 src/build_features.py     # Step 3 : ML + scénarios 2027
streamlit run app/main.py                # Application interactive
```

> Sur Windows, l'option `-X utf8` est nécessaire pour gérer les caractères spéciaux dans les noms de candidats.

---

## Structure du projet

```
election-project/
├── data/
│   ├── elections/          # 12 fichiers XLS/XLSX Ministère de l'Intérieur
│   └── population/         # estim-pop-dep-sexe-gca-1975-2024.xls (INSEE)
│
├── src/
│   ├── merge_demography.py # Fusion élections + démographie INSEE
│   ├── eda_analysis.py     # 10 figures d'analyse exploratoire
│   └── build_features.py   # Feature engineering, LOYO CV, clustering, scénarios
│
├── app/
│   ├── main.py             # Streamlit — page d'accueil
│   ├── data_loader.py      # Cache des données
│   └── pages/
│       ├── 1_Historique.py # Acte 1 : évolution 1995–2022
│       ├── 2_Demographie.py # Acte 2 : démographie et abstention
│       └── 3_2027.py       # Acte 3 : scénarios + simulateur interactif
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda.ipynb
│   └── 04_demography.ipynb
│
├── outputs/
│   ├── figures/            # 10 figures PNG (EDA + ML)
│   ├── tables/             # CSV : LOYO, clusters, scénarios, prédictions
│   └── models/             # ridge_pipeline.joblib + feat_cols.json
│
└── docs/
    └── methodology.md      # Méthodologie détaillée
```

---

## Résultats clés

| Indicateur | Valeur |
|-----------|--------|
| Abstention T1 1995 | ~21% |
| Abstention T1 2022 | ~26% |
| Tendance linéaire | +0.6 pp / an depuis 2007 |
| Corrélation % jeunes × abstention | r = +0.38 |
| Prédiction 2027 (baseline) | **~28.9%** |
| Intervalle scénarios 2027 | 26.3% – 30.4% |

---

## Modélisation

- **Validation :** Leave-One-Year-Out (LOYO) sur 6 années
- **Modèle final :** Ridge (le plus stable en généralisation inter-années, RMSE moyen ~4.7 pp)
- **Clustering :** KMeans k=4 sur métropole uniquement (silhouette = 0.29) — 4 profils politiques identifiables
- **Simulateur :** L'application Streamlit permet d'ajuster les paramètres en temps réel (sliders démographiques + contexte électoral)

---

## Sources

- Ministère de l'Intérieur — data.gouv.fr
- INSEE — estimations de population par département 1975–2024
- GeoJSON France : github.com/gregoiredavid/france-geojson

---

## Équipe

Projet réalisé par deux étudiants B3 YNOV dans le cadre du cours Fil Rouge IA & Data.
