"""
build_features.py
=================
Étape 3 — Modélisation ML

Deux axes :
  A. Régression (Ridge / RandomForest / GradientBoosting)
     → prédit le taux d'abstention T1 2027 par département
     → validation : Leave-One-Year-Out (LOYO)

  B. Clustering (KMeans)
     → identifie des profils de départements

  C. Scénarios 2027
     → baseline, abstention jeunes +5pp, remobilisation

Usage
-----
    python src/build_features.py
"""

import unicodedata
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import mean_squared_error, r2_score, silhouette_score

warnings.filterwarnings("ignore")

# ── Chemins ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DEMO_FILE = BASE_DIR / "outputs" / "elections_with_demography.csv"
CAND_FILE = BASE_DIR / "outputs" / "elections_candidats.csv"
FIG_DIR = BASE_DIR / "outputs" / "figures"
TABLE_DIR = BASE_DIR / "outputs" / "tables"
for _d in [FIG_DIR, TABLE_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

# ── Familles politiques ────────────────────────────────────────────────────────
# Noms en MAJUSCULES SANS ACCENT : la comparaison passe par normalize_name()
# pour absorber les variations de casse/accents entre les fichiers sources
# (ex. "SARKOZY Nicolas" en 2007+ vs "SARKOZY NICOLAS" ici).
FAMILLES = {
    "extreme_gauche": ["LAGUILLER ARLETTE", "BESANCENOT OLIVIER", "POUTOU PHILIPPE", "ARTHAUD NATHALIE"],
    "gauche":         ["JOSPIN LIONEL", "HUE ROBERT", "TAUBIRA CHRISTIANE", "ROYAL SEGOLENE",
                       "HOLLANDE FRANCOIS", "HAMON BENOIT", "MELENCHON JEAN-LUC",
                       "ROUSSEL FABIEN", "HIDALGO ANNE"],
    "ecologie":       ["VOYNET DOMINIQUE", "MAMERE NOEL", "DUFLOT CECILE", "JADOT YANNICK"],
    "centre":         ["BAYROU FRANCOIS", "MACRON EMMANUEL", "LASSALLE JEAN"],
    "droite":         ["CHIRAC JACQUES", "BALLADUR EDOUARD", "MADELIN ALAIN", "SARKOZY NICOLAS",
                       "FILLON FRANCOIS", "PECRESSE VALERIE"],
    "souverainiste":  ["VILLIERS DE PHILIPPE", "DE VILLIERS PHILIPPE", "DUPONT-AIGNAN NICOLAS",
                       "SAINT-JOSSE JEAN", "CHEVENEMENT JEAN-PIERRE"],
    "extreme_droite": ["LE PEN J.MARIE", "LE PEN JEAN-MARIE", "LE PEN MARINE", "MEGRET BRUNO",
                       "ZEMMOUR ERIC"],
}


def normalize_name(s: str) -> str:
    """Majuscules + suppression des accents (cf. eda_analysis.py)."""
    s = str(s).upper().strip()
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


FAMILLES_NORM = {
    fam: {normalize_name(nom) for nom in noms}
    for fam, noms in FAMILLES.items()
}


def get_famille(candidat: str) -> str:
    nom_norm = normalize_name(candidat)
    for fam, noms in FAMILLES_NORM.items():
        if nom_norm in noms:
            return fam
    return "autre"


def save_fig(name: str):
    path = FIG_DIR / f"{name}.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Figure : {path.name}")


# ═══════════════════════════════════════════════════════════════════════════════
# 1. FEATURE ENGINEERING
# ═══════════════════════════════════════════════════════════════════════════════

def build_regression_dataset(df_demo: pd.DataFrame, df_cand: pd.DataFrame) -> pd.DataFrame:
    """
    Dataset (dept × annee) T1 pour la régression.

    Cible   : taux_abstention
    Features: démographiques (année t)
              + lag_taux_abstention (valeur t-1)
              + lag_score_{famille} (valeur t-1)
              + prev_trend (variation d'abstention entre t-2 et t-1)

    Les features de lag garantissent l'absence de data leakage :
    aucune information de l'année t n'est utilisée sauf la démographie
    (connue à l'avance via les projections INSEE).
    """
    # T1 continental uniquement (pop_ens_total disponible)
    t1 = df_demo[(df_demo["tour"] == 1) & df_demo["pop_ens_total"].notna()].copy()
    t1 = t1.sort_values(["dept_code", "annee"]).reset_index(drop=True)

    # Scores par famille politique par (dept, annee) ──────────────────────────
    cand_t1 = df_cand[df_cand["tour"] == 1].copy()
    cand_t1["famille"] = cand_t1["candidat"].apply(get_famille)

    voix = cand_t1.groupby(["annee", "dept_code", "famille"])["voix"].sum().reset_index()
    expr = cand_t1.groupby(["annee", "dept_code"])["exprimes"].first().reset_index()
    voix = voix.merge(expr, on=["annee", "dept_code"])
    voix["score"] = (voix["voix"] / voix["exprimes"] * 100).round(2)

    pivot = voix.pivot_table(
        index=["annee", "dept_code"], columns="famille", values="score", aggfunc="sum"
    ).reset_index().fillna(0)
    pivot.columns.name = None
    fam_cols = [c for c in pivot.columns if c not in ("annee", "dept_code")]
    pivot.columns = ["annee", "dept_code"] + [f"score_{c}" for c in fam_cols]

    # Merge demo + scores famille ─────────────────────────────────────────────
    keep = ["annee", "dept_code", "dept_nom_election", "inscrits",
            "pct_jeunes", "pct_actifs", "pct_seniors", "ratio_seniors_jeunes",
            "taux_abstention", "pop_ens_total"]
    df = t1[keep].merge(pivot, on=["annee", "dept_code"], how="left")

    # Lag features (valeurs de l'élection précédente) ─────────────────────────
    lag_src = ["taux_abstention"] + [f"score_{c}" for c in fam_cols]
    df = df.sort_values(["dept_code", "annee"]).reset_index(drop=True)
    for col in lag_src:
        df[f"lag_{col}"] = df.groupby("dept_code")[col].shift(1)

    # Tendance entrante : variation entre t-2 et t-1 ──────────────────────────
    # = variation DÉJÀ OBSERVÉE entrant dans l'année t, sans leakage
    df["lag2_taux_abstention"] = df.groupby("dept_code")["taux_abstention"].shift(2)
    df["prev_trend"] = df["lag_taux_abstention"] - df["lag2_taux_abstention"]

    return df


def regression_feature_cols(df: pd.DataFrame) -> list:
    """
    Sélectionne les colonnes features pour la régression.
    Règle : uniquement données de t-1 ou antérieures, + démographie t (projectable).
    """
    demo = ["pct_jeunes", "pct_actifs", "pct_seniors", "ratio_seniors_jeunes"]
    lags = [c for c in df.columns if c.startswith("lag_taux_") or c.startswith("lag_score_")]
    trend = ["prev_trend"]
    return [c for c in demo + lags + trend if c in df.columns]


# ═══════════════════════════════════════════════════════════════════════════════
# 2. RÉGRESSION — Leave-One-Year-Out CV
# ═══════════════════════════════════════════════════════════════════════════════

def loyo_cv(df: pd.DataFrame, feat_cols: list) -> pd.DataFrame:
    """
    Validation temporelle : entraîne sur N-1 années, teste sur la Nème.
    Seules les années ayant des features complètes (≥ 2007) sont testées.
    """
    TARGET = "taux_abstention"
    valid = df.dropna(subset=feat_cols + [TARGET]).copy()
    years = sorted(valid["annee"].unique())

    # Modèles : Ridge (avec scaling), arbres (sans scaling)
    model_defs = {
        "Ridge": ("scaled", Ridge(alpha=1.0)),
        "RandomForest": ("raw", RandomForestRegressor(n_estimators=200, max_depth=5, random_state=42)),
        "GradientBoosting": ("raw", GradientBoostingRegressor(n_estimators=200, max_depth=3, random_state=42)),
    }

    rows = []
    for test_year in years:
        train = valid[valid["annee"] != test_year]
        test = valid[valid["annee"] == test_year]
        if len(train) < 20 or len(test) == 0:
            continue

        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(train[feat_cols].values)
        X_te_s = scaler.transform(test[feat_cols].values)
        X_tr_r = train[feat_cols].values
        X_te_r = test[feat_cols].values
        y_tr = train[TARGET].values
        y_te = test[TARGET].values

        for name, (mode, model) in model_defs.items():
            X_fit, X_pred = (X_tr_s, X_te_s) if mode == "scaled" else (X_tr_r, X_te_r)
            model.fit(X_fit, y_tr)
            y_hat = model.predict(X_pred)
            rows.append({
                "year": test_year,
                "model": name,
                "RMSE": round(np.sqrt(mean_squared_error(y_te, y_hat)), 3),
                "R²": round(r2_score(y_te, y_hat), 3),
                "n_test": len(y_te),
            })

    return pd.DataFrame(rows)


def train_final_rf(df: pd.DataFrame, feat_cols: list) -> RandomForestRegressor:
    """RandomForest entraîné sur toutes les années disponibles."""
    TARGET = "taux_abstention"
    valid = df.dropna(subset=feat_cols + [TARGET])
    model = RandomForestRegressor(n_estimators=500, max_depth=5, random_state=42)
    model.fit(valid[feat_cols].values, valid[TARGET].values)
    return model


def plot_loyo(results: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, metric in zip(axes, ["RMSE", "R²"]):
        pivot = results.pivot(index="year", columns="model", values=metric)
        pivot.plot(kind="bar", ax=ax, width=0.7)
        ax.set_title(f"{metric} — Leave-One-Year-Out CV")
        ax.set_xlabel("Année test")
        ax.set_ylabel(metric)
        ax.grid(axis="y", alpha=0.3)
        ax.legend(fontsize=9)
    plt.suptitle("Régression taux d'abstention T1 — Performances LOYO", fontsize=13)
    plt.tight_layout()
    save_fig("06_loyo_cv")


def plot_importances(model: RandomForestRegressor, feat_cols: list):
    imp = pd.Series(model.feature_importances_, index=feat_cols).sort_values()
    fig, ax = plt.subplots(figsize=(8, max(4, len(feat_cols) * 0.35)))
    imp.plot(kind="barh", ax=ax, color="#1f77b4", alpha=0.85)
    ax.set_title("Feature importance — RandomForest (modèle final)")
    ax.set_xlabel("MDI importance")
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    save_fig("07_feature_importance")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. CLUSTERING — Profils de départements
# ═══════════════════════════════════════════════════════════════════════════════

def build_clustering_dataset(df_demo: pd.DataFrame, df_cand: pd.DataFrame) -> pd.DataFrame:
    """
    Agrège l'historique 1995-2022 par département.
    Features : moyennes démographiques + scores moyens familles clés + delta abstention.
    """
    t1 = df_demo[(df_demo["tour"] == 1) & df_demo["pop_ens_total"].notna()].copy()

    base = t1.groupby("dept_code").agg(
        dept_nom=("dept_nom_election", "first"),
        mean_abstention=("taux_abstention", "mean"),
        std_abstention=("taux_abstention", "std"),
        mean_seniors=("pct_seniors", "mean"),
        mean_jeunes=("pct_jeunes", "mean"),
        mean_actifs=("pct_actifs", "mean"),
    ).reset_index()

    # Variation d'abstention sur la période complète
    piv = t1.pivot_table(index="dept_code", columns="annee", values="taux_abstention")
    if 1995 in piv.columns and 2022 in piv.columns:
        delta = (piv[2022] - piv[1995]).rename("delta_abstention")
        base = base.merge(delta, on="dept_code", how="left")

    # Score moyen des familles politiques principales
    cand_t1 = df_cand[df_cand["tour"] == 1].copy()
    cand_t1["famille"] = cand_t1["candidat"].apply(get_famille)
    voix = cand_t1.groupby(["annee", "dept_code", "famille"])["voix"].sum().reset_index()
    expr = cand_t1.groupby(["annee", "dept_code"])["exprimes"].first().reset_index()
    voix = voix.merge(expr, on=["annee", "dept_code"])
    voix["score"] = voix["voix"] / voix["exprimes"] * 100

    for fam in ["extreme_droite", "gauche", "centre"]:
        fam_mean = (
            voix[voix["famille"] == fam]
            .groupby("dept_code")["score"].mean()
            .rename(f"mean_{fam}")
        )
        base = base.merge(fam_mean, on="dept_code", how="left")

    return base.fillna(0)


def train_clustering(df_clust: pd.DataFrame, k_max: int = 9) -> tuple:
    """
    KMeans avec sélection automatique de k par silhouette score.
    Retourne (df avec colonne 'cluster', k optimal).
    """
    feat_cols = [c for c in df_clust.columns if c not in ("dept_code", "dept_nom")]
    X_s = StandardScaler().fit_transform(df_clust[feat_cols].values)

    K_range = range(2, k_max + 1)
    inertias, silhouettes = [], []
    for k in K_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_s)
        inertias.append(km.inertia_)
        silhouettes.append(silhouette_score(X_s, labels))

    best_k = list(K_range)[np.argmax(silhouettes)]
    print(f"  k optimal = {best_k}  (silhouette = {max(silhouettes):.3f})")

    km_final = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    df_out = df_clust.copy()
    df_out["cluster"] = km_final.fit_predict(X_s)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].plot(K_range, inertias, "o-", color="#1f77b4")
    axes[0].set_title("Inertie vs k")
    axes[0].set_xlabel("k")
    axes[0].set_ylabel("Inertie")
    axes[0].grid(alpha=0.3)

    axes[1].plot(K_range, silhouettes, "o-", color="#2ca02c")
    axes[1].axvline(best_k, color="red", ls="--", lw=1, label=f"k={best_k}")
    axes[1].set_title("Silhouette vs k")
    axes[1].set_xlabel("k")
    axes[1].set_ylabel("Silhouette score")
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    plt.suptitle("Choix du nombre de clusters — KMeans")
    plt.tight_layout()
    save_fig("08_clustering_choice")

    return df_out, best_k


# ═══════════════════════════════════════════════════════════════════════════════
# 4. SCÉNARIOS 2027
# ═══════════════════════════════════════════════════════════════════════════════

def generate_2027(df_reg: pd.DataFrame, model: RandomForestRegressor, feat_cols: list) -> pd.DataFrame:
    """
    Projections 2027 en 3 scénarios à partir des données 2022.

    Construction des features 2027 :
    - Démographie projetée (+1.2pp seniors / -0.8pp jeunes, tendance INSEE)
    - lag_* mis à jour avec les valeurs réelles 2022
    - prev_trend = variation observée 2017→2022
    """
    base = df_reg[df_reg["annee"] == 2022].copy()
    if base.empty:
        print("  [WARN] Données 2022 introuvables dans df_reg.")
        return pd.DataFrame()

    # prev_trend pour 2027 = variation 2017→2022
    # Calculé AVANT mise à jour des lags (lag_taux_abstention = 2017 ici)
    base["prev_trend"] = base["taux_abstention"] - base["lag_taux_abstention"]

    # Mise à jour des lags : t-1 pour 2027 = valeurs réelles 2022
    for col in feat_cols:
        if col.startswith("lag_"):
            src = col[4:]  # "lag_taux_abstention" → "taux_abstention"
            if src in base.columns:
                base[col] = base[src]

    # Projection démographique +5 ans (tendance INSEE)
    base["pct_seniors"] = (base["pct_seniors"] + 1.2).round(2)
    base["pct_jeunes"] = (base["pct_jeunes"] - 0.8).round(2)
    base["annee"] = 2027

    def predict(df_s: pd.DataFrame) -> pd.DataFrame:
        X = df_s[feat_cols].fillna(0).values
        df_s = df_s.copy()
        df_s["abstention_pred"] = model.predict(X).round(2)
        return df_s

    def score_national(df_s: pd.DataFrame) -> float:
        return round(
            (df_s["abstention_pred"] * df_s["inscrits"]).sum() / df_s["inscrits"].sum(), 2
        )

    # ── Scénario baseline ─────────────────────────────────────────────────────
    s_base = predict(base.copy())

    # ── Scénario abstention jeunes +5pp ──────────────────────────────────────
    # Hypothèse : davantage de jeunes non-inscrits/abstentionnistes
    s_jeunes = base.copy()
    s_jeunes["pct_jeunes"] += 4.0
    s_jeunes["lag_taux_abstention"] += 3.0
    s_jeunes = predict(s_jeunes)

    # ── Scénario remobilisation ──────────────────────────────────────────────
    # Hypothèse : choc politique (type 2002) → forte baisse de l'abstention
    s_remob = base.copy()
    s_remob["lag_taux_abstention"] -= 4.0
    s_remob["prev_trend"] -= 3.0
    s_remob = predict(s_remob)

    scenarios = {
        "baseline": s_base,
        "abstention_jeunes_+5pp": s_jeunes,
        "remobilisation_-4pp": s_remob,
    }

    # ── Synthèse nationale ────────────────────────────────────────────────────
    summary = pd.DataFrame([
        {
            "scenario": nom,
            "abstention_nationale_pred (%)": score_national(s),
            "dept_min (%)": round(s["abstention_pred"].min(), 2),
            "dept_max (%)": round(s["abstention_pred"].max(), 2),
        }
        for nom, s in scenarios.items()
    ])
    print("\nProjections 2027 :")
    print(summary.to_string(index=False))
    summary.to_csv(TABLE_DIR / "scenarios_2027.csv", index=False)

    # ── Visualisations ────────────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    ax = axes[0]
    colors = ["#1f77b4", "#e74c3c", "#2ca02c"]
    vals = summary["abstention_nationale_pred (%)"].values
    bars = ax.bar(summary["scenario"], vals, color=colors, alpha=0.85, width=0.5)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.3, f"{v:.1f}%",
                ha="center", fontsize=11, fontweight="bold")
    ax.set_title("Abstention nationale T1 2027 — Scénarios")
    ax.set_ylabel("Taux d'abstention prédit (%)")
    ax.set_ylim(0, 50)
    ax.grid(axis="y", alpha=0.3)

    ax = axes[1]
    for (nom, s), color in zip(scenarios.items(), colors):
        ax.hist(s["abstention_pred"], bins=20, alpha=0.5, label=nom, color=color, density=True)
    ax.set_title("Distribution par département — 2027")
    ax.set_xlabel("Abstention prédite (%)")
    ax.set_ylabel("Densité")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.2)

    plt.suptitle("Projections 2027 — Présidentielle T1", fontsize=13)
    plt.tight_layout()
    save_fig("09_scenarios_2027")

    # Prédictions détaillées par département
    pd.concat(
        [s[["dept_code", "dept_nom_election", "annee", "abstention_pred"]].assign(scenario=nom)
         for nom, s in scenarios.items()],
        ignore_index=True
    ).to_csv(TABLE_DIR / "predictions_2027_dept.csv", index=False)

    return summary


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("═" * 60)
    print("  Modélisation ML — Élections présidentielles 2027")
    print("═" * 60)

    df_demo = pd.read_csv(DEMO_FILE)
    df_cand = pd.read_csv(CAND_FILE)
    print(f"Chargé — démo : {df_demo.shape}  |  candidats : {df_cand.shape}")

    # ── 1. Feature engineering ─────────────────────────────────────────────────
    print("\n[1] Feature engineering...")
    df_reg = build_regression_dataset(df_demo, df_cand)
    feat_cols = regression_feature_cols(df_reg)
    print(f"  {len(feat_cols)} features : {feat_cols}")
    df_reg.to_csv(TABLE_DIR / "regression_dataset.csv", index=False)

    # ── 2. LOYO Cross-validation ───────────────────────────────────────────────
    print("\n[2] Leave-One-Year-Out CV...")
    cv = loyo_cv(df_reg, feat_cols)
    print(cv.to_string(index=False))
    cv.to_csv(TABLE_DIR / "loyo_cv_results.csv", index=False)
    plot_loyo(cv)

    # ── 3. Modèle final ────────────────────────────────────────────────────────
    print("\n[3] Entraînement modèle final (toutes années)...")
    model = train_final_rf(df_reg, feat_cols)
    plot_importances(model, feat_cols)

    # ── 4. Clustering ──────────────────────────────────────────────────────────
    print("\n[4] Clustering des départements...")
    df_clust = build_clustering_dataset(df_demo, df_cand)
    df_clust, best_k = train_clustering(df_clust)
    clust_feat = [c for c in df_clust.columns if c not in ("dept_code", "dept_nom", "cluster")]
    profiles = df_clust.groupby("cluster")[clust_feat].mean().round(2)
    print(f"\nProfils des {best_k} clusters :")
    print(profiles.to_string())
    df_clust[["dept_code", "dept_nom", "cluster"]].to_csv(TABLE_DIR / "dept_clusters.csv", index=False)
    profiles.to_csv(TABLE_DIR / "cluster_profiles.csv")

    # ── 5. Scénarios 2027 ──────────────────────────────────────────────────────
    print("\n[5] Scénarios 2027...")
    generate_2027(df_reg, model, feat_cols)

    print(f"\n✅ Terminé.")
    print(f"   Figures → {FIG_DIR}")
    print(f"   Tables  → {TABLE_DIR}")


if __name__ == "__main__":
    main()
