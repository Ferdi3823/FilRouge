import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CANDIDATS_FILE = BASE_DIR / "outputs" / "elections_candidats.csv"
DEMOGRAPHY_FILE = BASE_DIR / "outputs" / "elections_with_demography.csv"
FIG_DIR = BASE_DIR / "outputs" / "figures"
TABLE_DIR = BASE_DIR / "outputs" / "tables"
FIG_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)

# Palette cohérente pour les années
ANNEES = [1995, 2002, 2007, 2012, 2017, 2022]
PALETTE_ANNEES = dict(zip(ANNEES, sns.color_palette("tab10", len(ANNEES))))

# Familles politiques (candidats T1 principaux)
FAMILLES = {
    "Extrême gauche":  ["LAGUILLER ARLETTE", "BESANCENOT OLIVIER", "POUTOU PHILIPPE", "ARTHAUD NATHALIE"],
    "Gauche":          ["JOSPIN LIONEL", "HUE ROBERT", "TAUBIRA CHRISTIANE", "ROYAL SEGOLENE",
                        "HOLLANDE FRANCOIS", "HAMON BENOIT", "MELENCHON JEAN-LUC"],
    "Ecologie":        ["VOYNET DOMINIQUE", "MAMERE NOEL", "DUFLOT CECILE", "JADOT YANNICK"],
    "Centre":          ["BAYROU FRANCOIS", "MACRON EMMANUEL"],
    "Droite":          ["CHIRAC JACQUES", "BALLADUR EDOUARD", "MADELIN ALAIN", "SARKOZY NICOLAS",
                        "FILLON FRANCOIS"],
    "Souverainiste":   ["VILLIERS DE PHILIPPE", "DUPONT-AIGNAN NICOLAS", "SAINT-JOSSE JEAN",
                        "CHEVENEMENT JEAN-PIERRE"],
    "Extrême droite":  ["LE PEN J.MARIE", "LE PEN JEAN-MARIE", "LE PEN MARINE", "MEGRET BRUNO",
                        "ZEMMOUR ERIC"],
    "Autre":           [],
}

COULEURS_FAMILLES = {
    "Extrême gauche": "#d62728",
    "Gauche":         "#e84a5f",
    "Ecologie":       "#2ca02c",
    "Centre":         "#ff7f0e",
    "Droite":         "#1f77b4",
    "Souverainiste":  "#9467bd",
    "Extrême droite": "#7f7f7f",
    "Autre":          "#bcbd22",
}


def get_famille(candidat):
    for famille, noms in FAMILLES.items():
        if candidat in noms:
            return famille
    return "Autre"


def save_fig(name):
    path = FIG_DIR / f"{name}.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Figure sauvée : {path.name}")


# ──────────────────────────────────────────────────────────────────
# 1. Évolution de la participation nationale par année
# ──────────────────────────────────────────────────────────────────
def analyse_participation(df_demo):
    print("\n[1] Participation nationale...")

    # Agréger au niveau national par annee+tour
    natl = (
        df_demo.groupby(["annee", "tour"])
        .agg(inscrits=("inscrits", "sum"), votants=("votants", "sum"), abstentions=("abstentions", "sum"))
        .reset_index()
    )
    natl["taux_participation"] = natl["votants"] / natl["inscrits"] * 100
    natl["taux_abstention"] = natl["abstentions"] / natl["inscrits"] * 100
    natl["tour_label"] = natl["tour"].map({1: "Tour 1", 2: "Tour 2"})

    fig, ax = plt.subplots(figsize=(10, 5))
    for tour, grp in natl.groupby("tour"):
        label = f"Tour {tour}"
        color = "#1f77b4" if tour == 1 else "#ff7f0e"
        ax.plot(grp["annee"], grp["taux_participation"], marker="o", label=label, color=color, linewidth=2)
        for _, row in grp.iterrows():
            ax.annotate(f"{row['taux_participation']:.1f}%", (row["annee"], row["taux_participation"]),
                        textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8)

    ax.set_title("Évolution de la participation aux scrutins présidentiels (1995–2022)", fontsize=13)
    ax.set_xlabel("Année")
    ax.set_ylabel("Taux de participation (%)")
    ax.set_xticks(ANNEES)
    ax.legend()
    ax.set_ylim(50, 100)
    ax.grid(axis="y", alpha=0.3)
    save_fig("01_participation_nationale")

    # Sauvegarde table
    natl.to_csv(TABLE_DIR / "participation_nationale.csv", index=False)
    return natl


# ──────────────────────────────────────────────────────────────────
# 2. Scores nationaux des familles politiques au T1
# ──────────────────────────────────────────────────────────────────
def analyse_familles(df_cand):
    print("\n[2] Familles politiques au T1...")

    t1 = df_cand[df_cand["tour"] == 1].copy()
    t1["famille"] = t1["candidat"].apply(get_famille)

    # Score national : sum(voix) / sum(exprimes) par annee+famille
    natl = (
        t1.groupby(["annee", "famille"])
        .agg(voix=("voix", "sum"), exprimes=("exprimes", "sum"))
        .reset_index()
    )
    # exprimes est dupliqué par dept, on recalcule
    exprimes_natl = t1.groupby("annee").apply(
        lambda g: g.drop_duplicates(subset=["dept_code"])["exprimes"].sum(),
        include_groups=False,
    ).reset_index(name="exprimes_natl")
    natl = natl.merge(exprimes_natl, on="annee")
    natl["pct"] = natl["voix"] / natl["exprimes_natl"] * 100

    # Pivot pour stacked bar
    pivot = natl.pivot_table(index="annee", columns="famille", values="pct", aggfunc="sum").fillna(0)

    familles_order = [f for f in FAMILLES if f in pivot.columns] + [c for c in pivot.columns if c not in FAMILLES]
    pivot = pivot[familles_order]

    fig, ax = plt.subplots(figsize=(12, 6))
    bottom = np.zeros(len(pivot))
    for famille in pivot.columns:
        color = COULEURS_FAMILLES.get(famille, "#bcbd22")
        bars = ax.bar(pivot.index, pivot[famille], bottom=bottom, label=famille, color=color, alpha=0.85, width=3)
        for i, (val, bot) in enumerate(zip(pivot[famille], bottom)):
            if val > 3:
                ax.text(pivot.index[i], bot + val / 2, f"{val:.0f}%", ha="center", va="center",
                        fontsize=7, color="white", fontweight="bold")
        bottom += pivot[famille].values

    ax.set_title("Répartition des votes par famille politique – Tour 1 (1995–2022)", fontsize=13)
    ax.set_xlabel("Année")
    ax.set_ylabel("% des exprimés")
    ax.set_xticks(ANNEES)
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    ax.set_ylim(0, 105)
    ax.grid(axis="y", alpha=0.3)
    save_fig("02_familles_politiques_t1")

    natl.to_csv(TABLE_DIR / "scores_familles_t1.csv", index=False)
    return natl


# ──────────────────────────────────────────────────────────────────
# 3. Candidats finalistes et scores au T2
# ──────────────────────────────────────────────────────────────────
def analyse_t2(df_cand):
    print("\n[3] Résultats du second tour...")

    t2 = df_cand[df_cand["tour"] == 2].copy()

    # Score national T2 par candidat et par année
    exprimes_t2 = (
        t2.groupby("annee")
        .apply(lambda g: g.drop_duplicates(subset=["dept_code"])["exprimes"].sum(),
               include_groups=False)
        .reset_index(name="exprimes_natl")
    )
    scores = (
        t2.groupby(["annee", "candidat"])["voix"].sum()
        .reset_index()
        .merge(exprimes_t2, on="annee")
    )
    scores["pct"] = scores["voix"] / scores["exprimes_natl"] * 100

    fig, ax = plt.subplots(figsize=(11, 5))
    for annee, grp in scores.groupby("annee"):
        grp_s = grp.sort_values("pct", ascending=False)
        x = [annee - 1, annee + 1]
        y = grp_s["pct"].tolist()
        noms = grp_s["candidat"].tolist()
        color = COULEURS_FAMILLES.get(get_famille(noms[0]), "#1f77b4")
        ax.bar(annee - 1.1, y[0] if len(y) > 0 else 0, width=1.8,
               color=COULEURS_FAMILLES.get(get_famille(noms[0] if noms else ""), "#1f77b4"), alpha=0.85)
        ax.bar(annee + 1.1, y[1] if len(y) > 1 else 0, width=1.8,
               color=COULEURS_FAMILLES.get(get_famille(noms[1] if len(noms) > 1 else ""), "#ff7f0e"), alpha=0.85)
        if len(y) > 0:
            ax.text(annee - 1.1, y[0] + 0.5, f"{noms[0].split()[0]}\n{y[0]:.1f}%",
                    ha="center", fontsize=7.5, fontweight="bold")
        if len(y) > 1:
            ax.text(annee + 1.1, y[1] + 0.5, f"{noms[1].split()[0]}\n{y[1]:.1f}%",
                    ha="center", fontsize=7.5, fontweight="bold")

    ax.axhline(50, color="red", linestyle="--", linewidth=1, alpha=0.5, label="50%")
    ax.set_title("Résultats du second tour – Présidentielles françaises (1995–2022)", fontsize=13)
    ax.set_xlabel("Année")
    ax.set_ylabel("% des exprimés")
    ax.set_xticks(ANNEES)
    ax.set_ylim(0, 90)
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    save_fig("03_resultats_t2")

    scores.to_csv(TABLE_DIR / "resultats_t2.csv", index=False)
    return scores


# ──────────────────────────────────────────────────────────────────
# 4. Corrélation démographie × abstention par département
# ──────────────────────────────────────────────────────────────────
def analyse_demo_vs_abstention(df_demo):
    print("\n[4] Corrélation démographie × abstention...")

    # T1 uniquement, sans DOM/TOM (pop manquante)
    df = df_demo[(df_demo["tour"] == 1) & df_demo["pop_ens_total"].notna()].copy()

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

    vars_demo = [
        ("pct_seniors", "% de seniors (60+)", "#e74c3c"),
        ("pct_jeunes", "% de jeunes (0–39 ans)", "#27ae60"),
        ("pct_actifs", "% d'actifs (40–59 ans)", "#2980b9"),
    ]

    for ax, (var, label, color) in zip(axes, vars_demo):
        for annee, grp in df.groupby("annee"):
            ax.scatter(grp[var], grp["taux_abstention"], alpha=0.3, s=12,
                       color=PALETTE_ANNEES[annee], label=str(annee))

        # Ligne de tendance globale
        corr_data = df[[var, "taux_abstention"]].dropna()
        if len(corr_data) > 10:
            z = np.polyfit(corr_data[var], corr_data["taux_abstention"], 1)
            p = np.poly1d(z)
            xs = np.linspace(corr_data[var].min(), corr_data[var].max(), 100)
            ax.plot(xs, p(xs), color=color, linewidth=2, linestyle="--")
            r = corr_data[var].corr(corr_data["taux_abstention"])
            ax.set_title(f"{label}\nr = {r:.2f}", fontsize=10)

        ax.set_xlabel(label)
        if ax == axes[0]:
            ax.set_ylabel("Taux d'abstention (%)")
        ax.grid(alpha=0.2)

    handles, labels = axes[0].get_legend_handles_labels()
    # Déduplication des labels
    seen = set()
    unique_h, unique_l = [], []
    for h, l in zip(handles, labels):
        if l not in seen:
            unique_h.append(h)
            unique_l.append(l)
            seen.add(l)
    fig.legend(unique_h, unique_l, loc="lower center", ncol=6, fontsize=8,
               title="Année", bbox_to_anchor=(0.5, -0.05))

    fig.suptitle("Démographie et abstention par département (T1, 1995–2022)", fontsize=13, y=1.01)
    plt.tight_layout()
    save_fig("04_demo_vs_abstention")

    # Table de corrélations
    corr_table = []
    for var, label, _ in vars_demo:
        r = df[[var, "taux_abstention"]].dropna().corr().iloc[0, 1]
        corr_table.append({"variable": label, "correlation_pearson": round(r, 3)})
    pd.DataFrame(corr_table).to_csv(TABLE_DIR / "correlations_demo_abstention.csv", index=False)


# ──────────────────────────────────────────────────────────────────
# 5. Évolution de l'abstention par département (top hausse)
# ──────────────────────────────────────────────────────────────────
def analyse_evolution_departements(df_demo):
    print("\n[5] Évolution de l'abstention par département...")

    t1 = df_demo[df_demo["tour"] == 1].copy()
    pivot = t1.pivot_table(index="dept_nom_election", columns="annee", values="taux_abstention")
    pivot = pivot.dropna(how="any")

    # Hausse de l'abstention entre 1995 et 2022
    pivot["hausse"] = pivot[2022] - pivot[1995]
    top_hausse = pivot.nlargest(15, "hausse")
    top_baisse = pivot.nsmallest(10, "hausse")

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for ax, data, title, color in [
        (axes[0], top_hausse, "Top 15 hausses d'abstention (1995→2022)", "#e74c3c"),
        (axes[1], top_baisse, "Top 10 baisses d'abstention (1995→2022)", "#27ae60"),
    ]:
        data_sorted = data.sort_values("hausse")
        bars = ax.barh(data_sorted.index, data_sorted["hausse"], color=color, alpha=0.8)
        for bar, val in zip(bars, data_sorted["hausse"]):
            ax.text(val + 0.1, bar.get_y() + bar.get_height() / 2,
                    f"{val:+.1f}pp", va="center", fontsize=8)
        ax.set_title(title, fontsize=11)
        ax.set_xlabel("Variation en points de %")
        ax.grid(axis="x", alpha=0.3)
        ax.axvline(0, color="black", linewidth=0.8)

    plt.suptitle("Variation du taux d'abstention au T1 entre 1995 et 2022", fontsize=13)
    plt.tight_layout()
    save_fig("05_evolution_abstention_depts")

    pivot.to_csv(TABLE_DIR / "abstention_par_dept_annee.csv")


# ──────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────
def main():
    print("=== Analyse exploratoire — Présidentielles françaises 1995–2022 ===\n")

    df_cand = pd.read_csv(CANDIDATS_FILE)
    df_demo = pd.read_csv(DEMOGRAPHY_FILE)

    print(f"Candidats : {df_cand.shape[0]} lignes | Démographie : {df_demo.shape[0]} lignes")

    analyse_participation(df_demo)
    analyse_familles(df_cand)
    analyse_t2(df_cand)
    analyse_demo_vs_abstention(df_demo)
    analyse_evolution_departements(df_demo)

    print(f"\nToutes les figures sont dans : {FIG_DIR}")
    print(f"Tous les tableaux sont dans  : {TABLE_DIR}")


if __name__ == "__main__":
    main()
