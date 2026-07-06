"""
Acte 3 — Et 2027 ? Scénarios de projection.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import urllib.request
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from data_loader import (load_scenarios_2027, load_predictions_2027,
                         load_linear_prediction, load_participation_nationale,
                         load_sondages_2027)
from _style import inject_css, PLOTLY_BASE, XAXIS_BASE, YAXIS_BASE, LEGEND_BASE, carte_note, section_title

st.set_page_config(
    page_title="Acte 3 — Et 2027 ?",
    page_icon="🔮",
    layout="wide",
)
inject_css()

GEO_URL = (
    "https://raw.githubusercontent.com/gregoiredavid/"
    "france-geojson/master/departements-version-simplifiee.geojson"
)

@st.cache_data(ttl=3600)
def load_geojson():
    with urllib.request.urlopen(GEO_URL) as r:
        return json.loads(r.read().decode())


# ── Données ─────────────────────────────────────────────────────────────────────
df_scen = load_scenarios_2027()
df_pred = load_predictions_2027()
df_pred["dept_code"] = df_pred["dept_code"].astype(str).str.zfill(2)

try:
    df_linpred = load_linear_prediction()
except Exception:
    df_linpred = None

try:
    df_partic = load_participation_nationale()
except Exception:
    df_partic = None

try:
    df_sondages = load_sondages_2027()
except Exception:
    df_sondages = None

SCENARIOS = {
    "baseline":               ("Scénario de base",                 "#2a78d6"),
    "abstention_jeunes_+5pp": ("Désengagement des jeunes (+5 pp)", "#e34948"),
    "remobilisation_-4pp":    ("Remobilisation (−4 pp)",           "#1baf7a"),
    "sans_macron_2027":       ("2027 sans Macron",                  "#9b59b6"),
}

LABELS = {
    "baseline":               "Base",
    "abstention_jeunes_+5pp": "Jeunes −",
    "remobilisation_-4pp":    "Remob. +",
    "sans_macron_2027":       "Sans Macron",
}

# ── En-tête ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#a06c00 0%,#eda100 100%);
border-radius:10px;padding:28px 32px 22px;margin-bottom:24px;">
  <p style="color:rgba(255,255,255,0.6);font-size:0.72rem;font-weight:700;
  letter-spacing:1.5px;text-transform:uppercase;margin:0 0 6px;">Acte 3 / 3</p>
  <h1 style="color:#fff;font-size:1.7rem;margin:0 0 10px;border:none;">🔮 Et 2027 ?</h1>
  <p style="color:rgba(255,255,255,0.92);font-size:0.95rem;margin:0;max-width:640px;">
    Si la tendance se maintient, l'abstention au T1 2027 devrait dépasser
    <strong style="color:#fff;">28 %</strong>.
    Deux méthodes complémentaires, des fourchettes honnêtes, un simulateur interactif.
  </p>
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── Méthode 1 : régression linéaire nationale ─────────────────────────────────
section_title("📈 Méthode 1 — Tendance linéaire (2007–2022)",
              "Approche transparente avec intervalles de confiance 80% et 95%")
st.markdown(
    "La façon la plus honnête de projeter : une droite de tendance sur les 4 dernières élections. "
    "Les **intervalles de confiance** montrent l'incertitude réelle — ne croyez pas une prédiction ponctuelle."
)

if df_linpred is not None and df_partic is not None:
    t1_lin = df_linpred[df_linpred["tour"] == 1].iloc[0]
    t2_lin = df_linpred[df_linpred["tour"] == 2].iloc[0]

    # KPI fourchettes
    kc1, kc2 = st.columns(2)
    kc1.markdown(f"""
<div style="background:#fcfcfb;border:1px solid #e1e0d9;border-top:4px solid #2a78d6;
border-radius:8px;padding:20px;text-align:center;">
  <p style="color:#52514e;font-size:0.78rem;font-weight:600;letter-spacing:0.8px;
  text-transform:uppercase;margin:0 0 4px;">Abstention T1 2027</p>
  <p style="color:#0b0b0b;font-size:2rem;font-weight:700;margin:0;">{t1_lin['pred']:.1f} %</p>
  <p style="color:#2a78d6;font-size:0.85rem;margin:4px 0 0;">
    IC 80% : {t1_lin['ci80_low']:.1f} % – {t1_lin['ci80_high']:.1f} %
  </p>
  <p style="color:#898781;font-size:0.75rem;margin:2px 0 0;">
    IC 95% : {t1_lin['ci95_low']:.1f} % – {t1_lin['ci95_high']:.1f} %
  </p>
</div>""", unsafe_allow_html=True)

    kc2.markdown(f"""
<div style="background:#fcfcfb;border:1px solid #e1e0d9;border-top:4px solid #ff7f0e;
border-radius:8px;padding:20px;text-align:center;">
  <p style="color:#52514e;font-size:0.78rem;font-weight:600;letter-spacing:0.8px;
  text-transform:uppercase;margin:0 0 4px;">Abstention T2 2027</p>
  <p style="color:#0b0b0b;font-size:2rem;font-weight:700;margin:0;">{t2_lin['pred']:.1f} %</p>
  <p style="color:#e07020;font-size:0.85rem;margin:4px 0 0;">
    IC 80% : {t2_lin['ci80_low']:.1f} % – {t2_lin['ci80_high']:.1f} %
  </p>
  <p style="color:#898781;font-size:0.75rem;margin:2px 0 0;">
    IC 95% : {t2_lin['ci95_low']:.1f} % – {t2_lin['ci95_high']:.1f} %
  </p>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Graphique tendance linéaire
    ANNEES = [1995, 2002, 2007, 2012, 2017, 2022]
    partic_t1 = df_partic[df_partic["tour"] == 1].sort_values("annee")
    partic_t2 = df_partic[df_partic["tour"] == 2].sort_values("annee")

    fig_trend = go.Figure()

    for tour_df, t1_data, label, color in [
        (partic_t1, t1_lin, "Tour 1", "#2a78d6"),
        (partic_t2, t2_lin, "Tour 2", "#ff7f0e"),
    ]:
        x_hist = tour_df[tour_df["annee"] >= 2007]["annee"].values.astype(float)
        y_hist = tour_df[tour_df["annee"] >= 2007]["taux_abstention"].values
        slope, intercept = np.polyfit(x_hist, y_hist, 1)
        x_ext = np.linspace(2007, 2028, 200)
        y_ext = intercept + slope * x_ext

        # Bande IC 80%
        fig_trend.add_trace(go.Scatter(
            x=[2027, 2027], y=[t1_data["ci80_low"], t1_data["ci80_high"]],
            mode="lines",
            line=dict(color=color, width=12, dash="solid"),
            opacity=0.25, showlegend=False,
            hoverinfo="skip",
        ))
        # Bande IC 95%
        fig_trend.add_trace(go.Scatter(
            x=[2027, 2027], y=[t1_data["ci95_low"], t1_data["ci95_high"]],
            mode="lines",
            line=dict(color=color, width=6, dash="solid"),
            opacity=0.12, showlegend=False,
            hoverinfo="skip",
        ))
        # Droite de tendance
        fig_trend.add_trace(go.Scatter(
            x=x_ext, y=y_ext,
            mode="lines",
            line=dict(color=color, width=1.5, dash="dash"),
            showlegend=False, hoverinfo="skip",
        ))
        # Points observés
        fig_trend.add_trace(go.Scatter(
            x=tour_df["annee"], y=tour_df["taux_abstention"],
            mode="lines+markers",
            name=label,
            line=dict(color=color, width=2.5),
            marker=dict(size=8, color=color),
            hovertemplate=f"<b>{label} %{{x}}</b><br>Abstention : %{{y:.1f}} %<extra></extra>",
        ))
        # Point prédiction
        fig_trend.add_trace(go.Scatter(
            x=[2027], y=[t1_data["pred"]],
            mode="markers",
            marker=dict(size=14, color=color, symbol="star"),
            showlegend=False,
            hovertemplate=f"<b>{label} 2027</b><br>Prédiction : {t1_data['pred']:.1f}%<br>"
                          f"IC 80% : [{t1_data['ci80_low']:.1f}–{t1_data['ci80_high']:.1f}%]<extra></extra>",
        ))

    # ── Sondages 2027 sur la courbe ──────────────────────────────────────────────
    if df_sondages is not None:
        s_t1 = df_sondages[df_sondages["tour"] == 1]
        # Décale légèrement en x pour que les 2 points soient lisibles
        x_offsets = [-0.3, 0.3]
        colors_poll = ["#9b59b6", "#e34948"]
        symbols_poll = ["diamond", "triangle-up"]
        for (_, row), dx, pc, sym in zip(s_t1.iterrows(), x_offsets, colors_poll, symbols_poll):
            fig_trend.add_trace(go.Scatter(
                x=[2027 + dx],
                y=[row["intention_abstention"]],
                mode="markers",
                name=f"Sondage — {row['source']} ({row['date_label']})",
                marker=dict(size=13, color=pc, symbol=sym,
                            line=dict(width=1.5, color="#ffffff")),
                error_y=dict(type="constant", value=row["marge"],
                             color=pc, thickness=2, width=6),
                hovertemplate=(
                    f"<b>Sondage {row['date_label']}</b><br>"
                    f"Source : {row['source']}<br>"
                    f"Intention d'abstention T1 : {row['intention_abstention']:.1f} %<br>"
                    f"Marge : ±{row['marge']:.1f} pp<extra></extra>"
                ),
            ))

    fig_trend.update_layout(
        **PLOTLY_BASE,
        yaxis=dict(**YAXIS_BASE, ticksuffix=" %", range=[15, 48],
                   title="Taux d'abstention (%)"),
        xaxis=dict(**XAXIS_BASE, range=[1993, 2030], dtick=5,
                   title="Année de l'élection"),
        height=420,
        legend=dict(**LEGEND_BASE, y=1.08),
    )
    fig_trend.add_vline(x=2022.5, line_dash="dot", line_color="#52514e", line_width=1,
                        annotation_text="→ Projection", annotation_position="top right")
    st.plotly_chart(fig_trend, use_container_width=True)

    carte_note(
        f"T1 2027 — Tendance linéaire : {t1_lin['pred']:.1f}% [IC 80% : {t1_lin['ci80_low']:.1f}–{t1_lin['ci80_high']:.1f}%]. "
        "Les sondages d'intention d'abstention (losange violet, triangle rouge) convergent vers une fourchette 31–34%, "
        "au-dessus de la seule projection linéaire — signal d'une désaffection accélérée."
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # Renvoi vers la page dédiée aux sondages
    if df_sondages is not None:
        s_t1_ref = df_sondages[df_sondages["tour"] == 1]
        weights_ref = 1.0 / (s_t1_ref["marge"] ** 2)
        poll_consensus_ref = float((s_t1_ref["intention_abstention"] * weights_ref).sum() / weights_ref.sum())
        consensus_ref = round(0.5 * float(t1_lin["pred"]) + 0.5 * poll_consensus_ref, 1)
        st.markdown(f"""
<div style="background:#f8f3ff;border:1px solid #d9a8e8;border-radius:8px;
padding:16px 20px;display:flex;align-items:center;gap:16px;">
  <span style="font-size:1.8rem;">📊</span>
  <div>
    <p style="font-weight:600;color:#6a0080;font-size:0.92rem;margin:0 0 2px;">
      Sondages disponibles : {len(s_t1_ref)} instituts · Consensus ~{consensus_ref}%</p>
    <p style="color:#52514e;font-size:0.82rem;margin:0;">
      {' · '.join(f"{r['source']} ({r['intention_abstention']:.1f}%)" for _, r in s_t1_ref.iterrows())}
      — Analyse complète dans la page <strong>Baromètre 2027</strong> (menu gauche)
    </p>
  </div>
</div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

st.markdown("---")
section_title("🤖 Méthode 2 — Modèle Ridge par département",
              "3 scénarios prédéfinis · fourchette ±4.7 pp (RMSE LOYO du modèle)")
st.markdown("<br>", unsafe_allow_html=True)

# ── Tuiles scénarios ─────────────────────────────────────────────────────────────
# RMSE moyen du modèle Ridge en LOYO (~4.7 pp) → fourchette de confiance
RIDGE_RMSE = 4.1  # mis à jour après enrichissement avec législatives 2017+2022

st.markdown("### Les quatre scénarios")
st.caption("La fourchette [min–max] représente l'incertitude du modèle (±RMSE moyen en validation LOYO).")
c1, c2, c3, c4 = st.columns(4, gap="medium")

SCENARIO_SUBTITLES = {
    "baseline":               "Tendance actuelle maintenue",
    "abstention_jeunes_+5pp": "Abstention jeunes accélérée",
    "remobilisation_-4pp":    "Choc politique mobilisateur",
    "sans_macron_2027":       "Effondrement de l'électorat centriste",
}

for col, (sid, (label, color)) in zip([c1, c2, c3, c4], SCENARIOS.items()):
    row = df_scen[df_scen.scenario == sid].iloc[0]
    pred = row["abstention_nationale_pred (%)"]
    dmin = row["dept_min (%)"]
    dmax = row["dept_max (%)"]
    ci_low = max(0, pred - RIDGE_RMSE)
    ci_high = pred + RIDGE_RMSE
    subtitle = SCENARIO_SUBTITLES.get(sid, "")
    with col:
        st.markdown(f"""
<div style="background:#fcfcfb;border:1px solid #e1e0d9;border-top:4px solid {color};
border-radius:8px;padding:18px 16px 14px;text-align:center;">
  <p style="color:{color};font-size:0.72rem;font-weight:700;letter-spacing:0.8px;
  text-transform:uppercase;margin:0 0 3px;">{label}</p>
  <p style="color:#898781;font-size:0.73rem;margin:0 0 10px;line-height:1.3;">{subtitle}</p>
  <p style="color:#0b0b0b;font-size:2rem;font-weight:700;margin:0 0 2px;">{pred:.1f} %</p>
  <p style="color:{color};font-size:0.8rem;font-weight:600;margin:0 0 4px;">
      {ci_low:.0f} – {ci_high:.0f} %
  </p>
  <p style="color:#c3c2b7;font-size:0.72rem;margin:0;">
      depts : {dmin:.1f} – {dmax:.1f} %
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Graphique comparatif barres ─────────────────────────────────────────────────
section_title("Comparaison des scénarios")

fig_bar = go.Figure()
for sid, (label, color) in SCENARIOS.items():
    row = df_scen[df_scen.scenario == sid].iloc[0]
    fig_bar.add_trace(go.Bar(
        name=label,
        x=[LABELS[sid]],
        y=[row["abstention_nationale_pred (%)"]],
        marker_color=color,
        marker_line=dict(width=0),
        width=0.45,
        text=[f"{row['abstention_nationale_pred (%)']:.1f} %"],
        textposition="outside",
        hovertemplate=f"<b>{label}</b><br>Abstention : %{{y:.1f}} %<extra></extra>",
    ))

fig_bar.update_layout(
    **PLOTLY_BASE,
    barmode="group",
    yaxis=dict(**YAXIS_BASE, ticksuffix=" %", range=[0, 36]),
    xaxis=dict(**XAXIS_BASE, showgrid=False),
    legend=LEGEND_BASE,
    height=360,
)
st.plotly_chart(fig_bar, use_container_width=True)

carte_note(
    "Le scénario « 2027 sans Macron » prédit la plus forte abstention : "
    "l'effondrement de l'électorat centriste (~27% en 2022) vers des candidats sans équivalent "
    "devrait pousser une fraction des électeurs à l'abstention. "
    "L'écart entre remobilisation et sans-Macron illustre l'amplitude du risque électoral (±4 pp). "
    "Dans tous les cas, les évolutions lentes de démographie et d'habitudes électorales "
    "restent les principaux déterminants structurels."
)

st.markdown("<br>", unsafe_allow_html=True)

# ── Carte prédictions 2027 ───────────────────────────────────────────────────────
section_title("Carte des prédictions 2027",
              "Abstention prédite par département pour le scénario sélectionné")

scenario_choisi = st.radio(
    "Scénario à afficher sur la carte :",
    options=list(SCENARIOS.keys()),
    format_func=lambda s: SCENARIOS[s][0],
    horizontal=True,
)

df_carte = df_pred[df_pred.scenario == scenario_choisi].copy()

try:
    geojson = load_geojson()
    _, color = SCENARIOS[scenario_choisi]
    fig_map = px.choropleth(
        df_carte,
        geojson=geojson,
        locations="dept_code",
        featureidkey="properties.code",
        color="abstention_pred",
        hover_name="dept_nom_election",
        hover_data={"abstention_pred": ":.1f", "dept_code": False},
        color_continuous_scale=[
            [0.00, "#1baf7a"],  # vert — faible abstention
            [0.30, "#eda100"],  # orange — abstention moyenne
            [0.65, "#e87b4a"],  # orange foncé
            [1.00, "#c0392b"],  # rouge — forte abstention
        ],
        range_color=[18, 36],
        labels={"abstention_pred": "Abstention prédite (%)"},
    )
    fig_map.update_geos(fitbounds="locations", visible=False, bgcolor="#f5f4f2")
    fig_map.update_layout(
        paper_bgcolor="#f5f4f2",
        margin=dict(l=0, r=0, t=0, b=0),
        height=480,
        coloraxis_colorbar=dict(
            title="Abstention<br>prédite (%)",
            ticksuffix=" %",
            thickness=14,
            len=0.6,
            bgcolor="rgba(252,252,251,0.9)",
            borderwidth=0,
        ),
        hoverlabel=dict(bgcolor="white", bordercolor="#c3c2b7"),
    )
    st.plotly_chart(fig_map, use_container_width=True)
except Exception as e:
    st.warning(f"Carte non disponible : {e}")
    st.dataframe(df_carte.sort_values("abstention_pred", ascending=False))

carte_note(
    "Les prédictions sont établies à partir des features démographiques (% seniors, % jeunes, actifs) "
    "et des taux d'abstention des deux élections précédentes (2017, 2022). "
    "La carte est limitée aux départements pour lesquels toutes les données démographiques sont disponibles."
)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# ── Simulateur interactif ─────────────────────────────────────────────────────
st.markdown("---")
section_title("🎛️ Simulateur personnalisé",
              "Ajustez les paramètres — le modèle Ridge recalcule en temps réel")
st.markdown(
    "Ajustez les paramètres ci-dessous pour construire votre propre scénario 2027. "
    "Le modèle **Ridge** (le plus stable en validation temporelle) recalcule l'abstention en temps réel."
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = BASE_DIR / "outputs" / "models"
TABLE_DIR = BASE_DIR / "outputs" / "tables"

@st.cache_resource
def load_model_and_features():
    try:
        import joblib
        model = joblib.load(MODEL_DIR / "ridge_pipeline.joblib")
        with open(MODEL_DIR / "feat_cols.json", encoding="utf-8") as f:
            feat_cols = json.load(f)
        return model, feat_cols
    except Exception:
        return None, None

@st.cache_data
def load_baseline_features():
    try:
        df = pd.read_csv(TABLE_DIR / "regression_dataset.csv")
        return df[df["annee"] == 2022].copy()
    except Exception:
        return None

model_ridge, feat_cols = load_model_and_features()
df_base22 = load_baseline_features()

if model_ridge is None or df_base22 is None or df_base22.empty:
    st.warning("Modèle non disponible. Relancez `python src/build_features.py` pour le générer.")
else:
    col_l, col_r = st.columns([1, 1], gap="large")

    with col_l:
        st.markdown("**Contexte démographique**")
        delta_seniors = st.slider(
            "Évolution du % de seniors (60+)",
            min_value=-2.0, max_value=5.0, value=1.2, step=0.5,
            help="La tendance INSEE projette +1.2 pp en 5 ans. Augmentez pour accélérer le vieillissement."
        )
        delta_jeunes = st.slider(
            "Évolution du % de jeunes (0–39)",
            min_value=-5.0, max_value=2.0, value=-0.8, step=0.5,
            help="Évolution projetée de la part des 0–39 ans dans la population."
        )

    with col_r:
        st.markdown("**Contexte électoral**")
        delta_mobilisation = st.slider(
            "Choc de mobilisation (vs 2022)",
            min_value=-10.0, max_value=10.0, value=0.0, step=0.5,
            help="Positif = plus d'abstention, négatif = effet remobilisant (ex: 2002). "
                 "Modifie le lag_taux_abstention de référence."
        )
        delta_trend = st.slider(
            "Tendance entrante (variation 2017→2022)",
            min_value=-6.0, max_value=6.0, value=0.0, step=0.5,
            help="Représente l'accélération ou le ralentissement de la tendance d'abstention."
        )

    # Construction des features 2027 à partir de la baseline 2022
    sim_df = df_base22.copy()

    # Mise à jour des lags (t-1 pour 2027 = valeurs réelles 2022)
    for col in feat_cols:
        if col.startswith("lag_"):
            src = col[4:]
            if src in sim_df.columns:
                sim_df[col] = sim_df[src]

    # Application des deltas du simulateur
    sim_df["prev_trend"] = sim_df["taux_abstention"] - sim_df["lag_taux_abstention"]
    sim_df["pct_seniors"] = (sim_df["pct_seniors"] + delta_seniors).round(2)
    sim_df["pct_jeunes"] = (sim_df["pct_jeunes"] + delta_jeunes).round(2)
    sim_df["lag_taux_abstention"] = (sim_df["lag_taux_abstention"] + delta_mobilisation).round(2)
    sim_df["prev_trend"] = (sim_df["prev_trend"] + delta_trend).round(2)

    # Prédiction
    X_sim = sim_df[feat_cols].fillna(0).values
    sim_df["abstention_pred"] = model_ridge.predict(X_sim).round(2)

    score_sim = round(
        (sim_df["abstention_pred"] * sim_df["inscrits"]).sum() / sim_df["inscrits"].sum(), 2
    )
    score_base = df_scen[df_scen["scenario"] == "baseline"]["abstention_nationale_pred (%)"].iloc[0]
    delta_vs_base = round(score_sim - score_base, 2)
    sign = "+" if delta_vs_base >= 0 else ""
    arrow = "🔴" if delta_vs_base > 0.5 else ("🟢" if delta_vs_base < -0.5 else "🟡")

    st.markdown("<br>", unsafe_allow_html=True)
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Abstention simulée T1 2027", f"{score_sim:.1f} %")
    kpi2.metric("vs scénario de base", f"{sign}{delta_vs_base:.1f} pp", delta_color="inverse")
    kpi3.metric(
        "Résultat",
        f"{arrow} {'Hausse' if delta_vs_base > 0.5 else ('Baisse' if delta_vs_base < -0.5 else 'Stable')}",
    )

    # Carte du scénario simulé
    st.markdown("**Carte de votre scénario**")
    try:
        geojson_sim = load_geojson()
        fig_sim = px.choropleth(
            sim_df.assign(dept_code=sim_df["dept_code"].astype(str).str.zfill(2)),
            geojson=geojson_sim,
            locations="dept_code",
            featureidkey="properties.code",
            color="abstention_pred",
            hover_name="dept_nom_election",
            hover_data={"abstention_pred": ":.1f", "dept_code": False},
            color_continuous_scale=[[0.00, "#1baf7a"], [0.30, "#eda100"], [0.65, "#e87b4a"], [1.00, "#c0392b"]],
            range_color=[18, 36],
            labels={"abstention_pred": "Abstention prédite (%)"},
        )
        fig_sim.update_geos(fitbounds="locations", visible=False, bgcolor="#f5f4f2")
        fig_sim.update_layout(
            paper_bgcolor="#f5f4f2",
            margin=dict(l=0, r=0, t=0, b=0),
            height=430,
            coloraxis_colorbar=dict(
                title="Abstention<br>prédite (%)",
                ticksuffix=" %",
                thickness=14,
                len=0.6,
                bgcolor="rgba(252,252,251,0.9)",
                borderwidth=0,
            ),
            hoverlabel=dict(bgcolor="white", bordercolor="#c3c2b7"),
        )
        st.plotly_chart(fig_sim, use_container_width=True)
    except Exception as e:
        st.info(f"Carte non disponible ({e}). Tableau des 10 départements avec le plus d'abstention :")
        st.dataframe(
            sim_df[["dept_nom_election", "abstention_pred"]]
            .sort_values("abstention_pred", ascending=False)
            .head(10)
            .rename(columns={"dept_nom_election": "Département", "abstention_pred": "Abstention prédite (%)"})
            .reset_index(drop=True),
            use_container_width=True,
        )

    carte_note(
        "Le simulateur utilise le modèle Ridge entraîné sur 1995–2022 "
        "(le plus robuste en validation Leave-One-Year-Out). "
        "Les prédictions restent des projections : le contexte politique 2027 n'est pas modélisable à partir des seules données démographiques."
    )
