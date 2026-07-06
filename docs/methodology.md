# Méthodologie — Projet FilRouge

## Présidentielle française 1995–2022 : analyse & prédictions 2027

---

## 1. Sources de données

| Source | Fichier | Description |
|--------|---------|-------------|
| Ministère de l'Intérieur | 12 fichiers XLS/XLSX | Résultats par département, 1995–2022, T1 et T2 |
| INSEE | `estim-pop-dep-sexe-gca-1975-2024.xls` | Estimations de population par département, sexe et groupe d'âge, 1975–2024 |

Les données électorales sont disponibles sur data.gouv.fr.

---

## 2. Pipeline de traitement

### Étape 1 — Parsing des fichiers électoraux

Les fichiers du Ministère ont 4 formats différents selon les années :

| Années | Format | Particularité |
|--------|--------|---------------|
| 1995–2012 | Format A | Feuille `Départements`, en-têtes ligne 0 |
| 2017 | Format B | 3 lignes vides avant les en-têtes |
| 2022 T1 | Format C | Granularité bureau de vote, aggrégation requise |
| 2022 T2 | Format D | Granularité commune, 2 candidats par ligne |

**Sortie :** `outputs/elections_dept.csv`, `outputs/elections_candidats.csv`

### Étape 2 — Fusion démographique

Le fichier INSEE présente une structure multi-feuille (une par année) avec 4 lignes d'en-têtes imbriqués.

**Normalisation des codes département :**
- Format électoral vers INSEE : `ZA->971`, `ZB->972`, `ZC->973`, `ZD->974`, `ZM->976`
- `1` -> `01`, `2A` conservé

**Indicateurs dérivés calculés :**
- `pct_jeunes` : % de la population âgée de 0–39 ans
- `pct_actifs` : % de la population âgée de 40–59 ans
- `pct_seniors` : % de la population âgée de 60 ans et plus
- `taux_participation` : votants / inscrits x 100
- `taux_abstention` : abstentions / inscrits x 100

**Sortie :** `outputs/elections_with_demography.csv` (1240 lignes x 21 colonnes)

### Étape 3 — Modélisation

#### Feature engineering

Dataset `(département x année)` avec :
- Features démographiques (année t, projectable via INSEE)
- `lag_taux_abstention` : taux d'abstention de l'élection précédente
- `lag_score_{famille}` : scores politiques de l'élection précédente
- `prev_trend` : variation d'abstention entre t-2 et t-1

La règle anti-fuite de données est strictement appliquée : aucune information de l'année cible n'est utilisée comme feature.

#### Validation temporelle (Leave-One-Year-Out)

Avec seulement 6 années électorales, on utilise la LOYO : pour chaque année de test, le modèle est entraîné sur les 5 autres années.

**Résultats LOYO (RMSE moyen, T1) :**

| Modèle | RMSE moyen | R² moyen |
|--------|-----------|----------|
| Ridge | ~4.7 pp | ~ -3.3 |
| RandomForest | ~5.4 pp | ~ -7.1 |
| GradientBoosting | ~5.0 pp | ~ -5.8 |

**Interprétation des R² négatifs :** les R² négatifs reflètent la difficulté à généraliser entre années électorales. Cela ne signifie pas que les modèles sont inutiles, mais que leurs prédictions doivent être interprétées avec une large incertitude.

**Choix du modèle :** Ridge est retenu pour les projections 2027 (RMSE moyen le plus bas en LOYO).

#### Clustering des départements (métropole uniquement)

Les DOM sont exclus pour éviter un clustering trivial métropole/outre-mer.

**Méthode :** KMeans, k optimal sélectionné par score de silhouette (testé de 2 à 9).
**Résultat :** k=4 clusters (silhouette ~0.29) :

| Cluster | Abstention moy. | Profil |
|---------|-----------------|--------|
| 0 | ~21% | Forte extrême droite, peu de seniors |
| 1 | ~19% | Forte gauche, très seniors |
| 2 | ~32% | Très forte abstention, peu de Centre |
| 3 | ~22% | Jeunes, gauche + centre fort (métropoles) |

---

## 3. Scénarios de projection 2027

| Scénario | Hypothèse | Abstention prédite |
|----------|-----------|-------------------|
| Baseline | Tendances démographiques actuelles | ~28.9% |
| Désengagement des jeunes | +4 pp part des jeunes + +3 pp lag abstention | ~30.4% |
| Remobilisation | -4 pp lag abstention + -3 pp tendance | ~26.3% |

---

## 4. Limites et perspectives

**Limites identifiées :**
1. Peu d'observations temporelles (6 années) — validation LOYO peu robuste
2. Variables contextuelles absentes : popularité des candidats, contexte économique
3. Données socio-économiques non intégrées (chômage, revenus, éducation)

**Pistes d'amélioration :**
- Intégrer des données socio-économiques INSEE par département
- Modèles à effets fixes département (panel data)
- Ajouter les sondages pré-électoraux comme variables exogènes

---

## 5. Stack technique

- **Python 3.11** — pandas, numpy, scikit-learn, scipy, matplotlib, seaborn
- **Streamlit** — application web interactive
- **Plotly** — visualisations interactives
- **joblib** — sérialisation du modèle Ridge
- **Jupyter Notebooks** — documentation de l'analyse exploratoire
