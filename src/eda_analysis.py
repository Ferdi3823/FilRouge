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
# 4. Corrélation démographie × abstention — graphique unique
# ──────────────────────────────────────────────────────────────────
def analyse_demo_vs_abstention(df_demo):
    print("\n[4] Corrélation démographie × abstention...")

    # T1 uniquement, sans DOM/TOM (pop manquante)
    df = df_demo[(df_demo["tour"] == 1) & df_demo["pop_ens_total"].notna()].copy()
    data = df[["pct_jeunes", "taux_abstention"]].dropna()

    fig, ax = plt.subplots(figsize=(10, 6))

    # Tous les points : tous depts × toutes années, sans distinction
    ax.scatter(data["pct_jeunes"], data["taux_abstention"],
               alpha=0.35, s=18, color="#4a90d9", edgecolors="none")

    # Ligne de tendance globale
    z = np.polyfit(data["pct_jeunes"], data["taux_abstention"], 1)
    p = np.poly1d(z)
    xs = np.linspace(data["pct_jeunes"].min(), data["pct_jeunes"].max(), 200)
    ax.plot(xs, p(xs), color="#e74c3c", linewidth=2.5, linestyle="--", label="Tendance globale")

    r = data["pct_jeunes"].corr(data["taux_abstention"])
    n = len(data)

    ax.set_title(
        f"% de jeunes (0–39 ans) vs taux d'abstention par département\n"
        f"Présidentielles T1, 1995–2022 — tous départements confondus   (r = {r:.2f})",
        fontsize=12,
    )
    ax.set_xlabel("% de la population âgée de 0 à 39 ans")
    ax.set_ylabel("Taux d'abstention (%)")
    ax.legend(fontsize=10)
    ax.grid(alpha=0.2)
    ax.annotate(f"n = {n} observations (6 scrutins × ~96 depts)",
                xy=(0.98, 0.04), xycoords="axes fraction",
                ha="right", fontsize=8, color="grey")

    plt.tight_layout()
    save_fig("04_demo_vs_abstention")

    # Table de corrélations par groupe
    corr_table = []
    for var, label in [("pct_seniors", "% seniors (60+)"),
                        ("pct_jeunes", "% jeunes (0–39)"),
                        ("pct_actifs", "% actifs (40–59)")]:
        r_grp = df[[var, "taux_abstention"]].dropna().corr().iloc[0, 1]
        corr_table.append({"variable": label, "correlation_pearson": round(r_grp, 3)})
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
# 6. Tous les groupes d'âge (0-19 → 75+) vs abstention
# ──────────────────────────────────────────────────────────────────
def analyse_tous_groupes_age(df_demo):
    print("\n[6] Tous les groupes d'âge vs abstention...")

    df = df_demo[(df_demo["tour"] == 1) & df_demo["pop_ens_total"].notna()].copy()
    pop = df["pop_ens_total"].replace(0, np.nan)

    groupes = {
        "0–19 ans":  ("pop_ens_0_19",  "#2ecc71"),
        "20–39 ans": ("pop_ens_20_39", "#27ae60"),
        "40–59 ans": ("pop_ens_40_59", "#3498db"),
        "60–74 ans": ("pop_ens_60_74", "#e67e22"),
        "75 ans +":  ("pop_ens_75p",   "#e74c3c"),
    }

    fig, ax = plt.subplots(figsize=(11, 6))

    corr_results = {}
    for label, (col, color) in groupes.items():
        if col not in df.columns:
            continue
        pct = (df[col] / pop * 100).rename("pct")
        data = pd.concat([pct, df["taux_abstention"]], axis=1).dropna()

        ax.scatter(data["pct"], data["taux_abstention"],
                   alpha=0.25, s=14, color=color, label=label)

        z = np.polyfit(data["pct"], data["taux_abstention"], 1)
        p = np.poly1d(z)
        xs = np.linspace(data["pct"].min(), data["pct"].max(), 200)
        r = data["pct"].corr(data["taux_abstention"])
        ax.plot(xs, p(xs), color=color, linewidth=2, linestyle="--", alpha=0.9)

        corr_results[label] = round(r, 3)

    # Légende enrichie avec le r de chaque groupe
    handles, labels_leg = ax.get_legend_handles_labels()
    new_labels = [f"{l}  (r = {corr_results.get(l, '?'):.2f})" for l in labels_leg]
    ax.legend(handles, new_labels, fontsize=9, title="Groupe d'âge", loc="upper right")

    ax.set_title(
        "Tous les groupes d'âge vs taux d'abstention par département\n"
        "Présidentielles T1, 1995–2022 — tous départements confondus",
        fontsize=12,
    )
    ax.set_xlabel("% de la population dans le groupe d'âge")
    ax.set_ylabel("Taux d'abstention (%)")
    ax.grid(alpha=0.2)
    ax.annotate(f"n ≈ {len(df)} observations par groupe (6 scrutins × ~96 depts)",
                xy=(0.98, 0.04), xycoords="axes fraction",
                ha="right", fontsize=8, color="grey")

    plt.tight_layout()
    save_fig("06_tous_groupes_age_vs_abstention")

    pd.DataFrame([{"groupe": k, "correlation_pearson": v}
                  for k, v in corr_results.items()]).to_csv(
        TABLE_DIR / "correlations_groupes_age_abstention.csv", index=False
    )


# ──────────────────────────────────────────────────────────────────
# 7. Courbe globale — tous groupes d'âge fusionnés vs abstention
# ──────────────────────────────────────────────────────────────────
def analyse_courbe_globale(df_demo):
    print("\n[7] Courbe globale tous groupes d'âge vs abstention...")

    df = df_demo[(df_demo["tour"] == 1) & df_demo["pop_ens_total"].notna()].copy()
    pop = df["pop_ens_total"].replace(0, np.nan)

    groupes = {
        "0–19 ans":  ("pop_ens_0_19",  "#2ecc71"),
        "20–39 ans": ("pop_ens_20_39", "#27ae60"),
        "40–59 ans": ("pop_ens_40_59", "#3498db"),
        "60–74 ans": ("pop_ens_60_74", "#e67e22"),
        "75 ans +":  ("pop_ens_75p",   "#e74c3c"),
    }

    # Calcul de la corrélation et de l'abstention moyenne pour chaque groupe
    records = []
    for label, (col, color) in groupes.items():
        if col not in df.columns:
            continue
        pct = (df[col] / pop * 100).rename("pct")
        data = pd.concat([pct, df["taux_abstention"]], axis=1).dropna()
        r = data["pct"].corr(data["taux_abstention"])
        records.append({
            "groupe": label,
            "color":  color,
            "r":      r,
            "pct_moyen": data["pct"].mean(),
            "abstention_moy": data["taux_abstention"].mean(),
            "data": data,
        })

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # — Panneau gauche : corrélation par tranche d'âge (ordonnée par âge croissant)
    ax1 = axes[0]
    labels = [r["groupe"] for r in records]
    corrs  = [r["r"]      for r in records]
    colors = [r["color"]  for r in records]

    bars = ax1.barh(labels, corrs, color=colors, alpha=0.85, edgecolor="white")
    for bar, val in zip(bars, corrs):
        ax1.text(val + (0.01 if val >= 0 else -0.01),
                 bar.get_y() + bar.get_height() / 2,
                 f"r = {val:+.2f}", va="center",
                 ha="left" if val >= 0 else "right", fontsize=9, fontweight="bold")
    ax1.axvline(0, color="black", linewidth=1)
    ax1.set_xlim(-0.6, 0.7)
    ax1.set_xlabel("Corrélation de Pearson avec le taux d'abstention")
    ax1.set_title("Corrélation tranche d'âge × abstention\n(positif = plus d'abstention)", fontsize=10)
    ax1.grid(axis="x", alpha=0.25)

    # — Panneau droit : nuage global avec tendance par groupe, X = âge médian de la tranche
    ax2 = axes[1]
    ages_medians = [9, 29, 49, 67, 80]  # milieux des tranches 0-19, 20-39, 40-59, 60-74, 75+
    for rec, age_med in zip(records, ages_medians):
        ax2.scatter([age_med] * len(rec["data"]),
                    rec["data"]["taux_abstention"],
                    alpha=0.15, s=10, color=rec["color"])
        ax2.scatter(age_med, rec["abstention_moy"],
                    s=120, color=rec["color"], edgecolors="black",
                    linewidth=1.2, zorder=5, label=rec["groupe"])

    # Courbe lissée reliant les moyennes
    moys_x = ages_medians
    moys_y = [r["abstention_moy"] for r in records]
    z = np.polyfit(moys_x, moys_y, 2)           # polynôme degré 2
    p2 = np.poly1d(z)
    xs = np.linspace(min(moys_x) - 5, max(moys_x) + 5, 300)
    ax2.plot(xs, p2(xs), color="black", linewidth=2.5, linestyle="--",
             label="Tendance globale (poly. deg. 2)", zorder=6)

    ax2.set_xlabel("Âge médian de la tranche")
    ax2.set_ylabel("Taux d'abstention (%)")
    ax2.set_title("Abstention moyenne par tranche d'âge\n(points = depts, losanges = moyenne)", fontsize=10)
    ax2.set_xticks(ages_medians)
    ax2.set_xticklabels(["0–19\n(9)", "20–39\n(29)", "40–59\n(49)", "60–74\n(67)", "75+\n(80)"])
    ax2.legend(fontsize=8, loc="upper right")
    ax2.grid(alpha=0.2)

    fig.suptitle(
        "Modélisation globale : relation entre tranche d'âge et taux d'abstention\n"
        "Présidentielles T1, 1995–2022",
        fontsize=13,
    )
    plt.tight_layout()
    save_fig("07_courbe_globale_tous_groupes")


# ──────────────────────────────────────────────────────────────────
# 9. Prédiction participation 2027 (régression linéaire depuis 2007)
# ──────────────────────────────────────────────────────────────────
def prediction_participation_2027(df_demo):
    print("\n[9] Prédiction participation 2027...")

    # Agrégation nationale par année + tour
    natl = (
        df_demo.groupby(["annee", "tour"])
        .agg(inscrits=("inscrits", "sum"), votants=("votants", "sum"))
        .reset_index()
    )
    natl["taux_participation"] = natl["votants"] / natl["inscrits"] * 100

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

    for ax, tour in zip(axes, [1, 2]):
        df_tour = natl[natl["tour"] == tour].sort_values("annee")

        # Tous les points historiques (contexte)
        hist_all = df_tour[df_tour["annee"] <= 2022]
        ax.scatter(hist_all["annee"], hist_all["taux_participation"],
                   color="grey", s=60, zorder=3, label="Données 1995–2022")

        # Points 2007–2022 utilisés pour la régression
        reg_df = df_tour[df_tour["annee"] >= 2007]
        x = reg_df["annee"].values
        y = reg_df["taux_participation"].values
        n = len(x)

        # Régression linéaire (numpy)
        coeffs = np.polyfit(x, y, 1)
        a, b = coeffs
        poly = np.poly1d(coeffs)

        # Résidus et erreur standard
        y_hat = poly(x)
        residuals = y - y_hat
        mse = np.sum(residuals ** 2) / (n - 2)
        x_mean = x.mean()
        ss_x = np.sum((x - x_mean) ** 2)

        # Valeur prédite 2027
        x_pred = 2027
        y_pred = poly(x_pred)

        # Intervalle de prédiction (t critique à 95%, df = n-2)
        from scipy import stats
        t_crit = stats.t.ppf(0.975, df=n - 2)
        se_pred = np.sqrt(mse * (1 + 1/n + (x_pred - x_mean)**2 / ss_x))
        ci_low  = y_pred - t_crit * se_pred
        ci_high = y_pred + t_crit * se_pred

        # Ligne de régression étendue jusqu'à 2027
        xs = np.linspace(2007, 2028, 300)
        ax.plot(xs, poly(xs), color="#3498db", linewidth=2,
                linestyle="--", label=f"Tendance 2007–2022\n(y = {a:+.2f}x {b:+.0f})")

        # Points de régression surlignés
        ax.scatter(x, y, color="#3498db", s=80, zorder=4)

        # Point de prédiction 2027
        ax.scatter(x_pred, y_pred, color="#e74c3c", s=160,
                   zorder=5, marker="*", label=f"Prédiction 2027 : {y_pred:.1f}%")

        # Intervalle de confiance
        ax.fill_between([x_pred - 0.3, x_pred + 0.3],
                        [ci_low, ci_low], [ci_high, ci_high],
                        color="#e74c3c", alpha=0.2)
        ax.vlines(x_pred, ci_low, ci_high, color="#e74c3c", linewidth=2, alpha=0.6)
        ax.annotate(f"IC 95%\n[{ci_low:.1f}% – {ci_high:.1f}%]",
                    xy=(x_pred + 0.3, y_pred), fontsize=8.5,
                    color="#e74c3c", va="center")

        ax.set_title(f"Tour {tour} — Prédiction 2027", fontsize=11)
        ax.set_xlabel("Année")
        if tour == 1:
            ax.set_ylabel("Taux de participation (%)")
        ax.set_xticks(list(ANNEES) + [2027])
        ax.set_xlim(1993, 2031)
        ax.set_ylim(50, 100)
        ax.axvline(2022.5, color="black", linewidth=0.8, linestyle=":", alpha=0.5)
        ax.legend(fontsize=8.5, loc="lower left")
        ax.grid(axis="y", alpha=0.25)

        print(f"  Tour {tour} — prédiction : {y_pred:.1f}%  IC95% [{ci_low:.1f}% – {ci_high:.1f}%]")

    fig.suptitle(
        "Prédiction du taux de participation pour 2027\n"
        "Régression linéaire sur les scrutins 2007–2022",
        fontsize=13,
    )
    plt.tight_layout()
    save_fig("09_prediction_participation_2027")


# ──────────────────────────────────────────────────────────────────
# 10. Prédiction abstention 2027 (régression linéaire depuis 2007)
# ──────────────────────────────────────────────────────────────────
def prediction_abstention_2027(df_demo):
    print("\n[10] Prédiction abstention 2027...")

    from scipy import stats

    natl = (
        df_demo.groupby(["annee", "tour"])
        .agg(inscrits=("inscrits", "sum"), abstentions=("abstentions", "sum"))
        .reset_index()
    )
    natl["taux_abstention"] = natl["abstentions"] / natl["inscrits"] * 100

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

    for ax, tour in zip(axes, [1, 2]):
        df_tour = natl[natl["tour"] == tour].sort_values("annee")

        # Tous les points historiques (contexte grisé)
        hist_all = df_tour[df_tour["annee"] <= 2022]
        ax.scatter(hist_all["annee"], hist_all["taux_abstention"],
                   color="grey", s=60, zorder=3, label="Données 1995–2022")

        # Points 2007–2022 pour la régression
        reg_df = df_tour[df_tour["annee"] >= 2007]
        x = reg_df["annee"].values.astype(float)
        y = reg_df["taux_abstention"].values
        n = len(x)

        coeffs = np.polyfit(x, y, 1)
        a, b = coeffs
        poly = np.poly1d(coeffs)

        y_hat  = poly(x)
        mse    = np.sum((y - y_hat) ** 2) / (n - 2)
        x_mean = x.mean()
        ss_x   = np.sum((x - x_mean) ** 2)

        x_pred  = 2027.0
        y_pred  = poly(x_pred)
        t_crit  = stats.t.ppf(0.975, df=n - 2)
        se_pred = np.sqrt(mse * (1 + 1/n + (x_pred - x_mean)**2 / ss_x))
        ci_low  = y_pred - t_crit * se_pred
        ci_high = y_pred + t_crit * se_pred

        # Ligne de tendance étendue à 2027
        xs = np.linspace(2007, 2028, 300)
        ax.plot(xs, poly(xs), color="#e67e22", linewidth=2, linestyle="--",
                label=f"Tendance 2007–2022\n(y = {a:+.2f}x {b:+.0f})")

        # Points de régression surlignés
        ax.scatter(x, y, color="#e67e22", s=80, zorder=4)

        # Prédiction 2027
        ax.scatter(x_pred, y_pred, color="#c0392b", s=160,
                   zorder=5, marker="*", label=f"Prédiction 2027 : {y_pred:.1f}%")

        # Intervalle de confiance
        ax.vlines(x_pred, ci_low, ci_high, color="#c0392b", linewidth=2, alpha=0.6)
        ax.fill_between([x_pred - 0.3, x_pred + 0.3],
                        [ci_low, ci_low], [ci_high, ci_high],
                        color="#c0392b", alpha=0.2)
        ax.annotate(f"IC 95%\n[{ci_low:.1f}% – {ci_high:.1f}%]",
                    xy=(x_pred + 0.3, y_pred), fontsize=8.5,
                    color="#c0392b", va="center")

        ax.set_title(f"Tour {tour} — Prédiction 2027", fontsize=11)
        ax.set_xlabel("Année")
        if tour == 1:
            ax.set_ylabel("Taux d'abstention (%)")
        ax.set_xticks(list(ANNEES) + [2027])
        ax.set_xlim(1993, 2031)
        ax.set_ylim(0, 50)
        ax.axvline(2022.5, color="black", linewidth=0.8, linestyle=":", alpha=0.5)
        ax.legend(fontsize=8.5, loc="upper left")
        ax.grid(axis="y", alpha=0.25)

        print(f"  Tour {tour} — prédiction : {y_pred:.1f}%  IC95% [{ci_low:.1f}% – {ci_high:.1f}%]")

    fig.suptitle(
        "Prédiction du taux d'abstention pour 2027\n"
        "Régression linéaire sur les scrutins 2007–2022",
        fontsize=13,
    )
    plt.tight_layout()
    save_fig("10_prediction_abstention_2027")


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
    analyse_tous_groupes_age(df_demo)
    analyse_courbe_globale(df_demo)
    prediction_participation_2027(df_demo)
    prediction_abstention_2027(df_demo)

    print(f"\nToutes les figures sont dans : {FIG_DIR}")
    print(f"Tous les tableaux sont dans  : {TABLE_DIR}")


if __name__ == "__main__":
    main()
