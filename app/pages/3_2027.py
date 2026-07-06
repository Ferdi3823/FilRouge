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
from data_loader import load_scenarios_2027, load_predictions_2027
from _style import inject_css, PLOTLY_BASE, XAXIS_BASE, YAXIS_BASE, LEGEND_BASE, carte_note

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

SCENARIOS = {
    "baseline":              ("Scénario de base",                "#2a78d6"),
    "abstention_jeunes_+5pp": ("Désengagement des jeunes (+5 pp)", "#e34948"),
    "remobilisation_-4pp":   ("Remobilisation (−4 pp)",           "#1baf7a"),
}

LABELS = {
    "baseline":              "Base",
    "abstention_jeunes_+5pp": "Jeunes −",
    "remobilisation_-4pp":   "Remob. +",
}

# ── En-tête ─────────────────────────────────────────────────────────────────────
st.markdown("## 🔮 Acte 3 — Et 2027 ?")
st.markdown(
    "Un modèle Random Forest entraîné sur les données 1995–2022 projette l'abstention au premier tour 2027. "
    "Trois hypothèses sont testées : une trajectoire **neutre**, un **décrochage des jeunes** et une **remobilisation**."
)
st.markdown("<br>", unsafe_allow_html=True)

# ── Tuiles scénarios ─────────────────────────────────────────────────────────────
st.markdown("### Les trois scénarios")
c1, c2, c3 = st.columns(3, gap="large")

for col, (sid, (label, color)) in zip([c1, c2, c3], SCENARIOS.items()):
    row = df_scen[df_scen.scenario == sid].iloc[0]
    pred = row["abstention_nationale_pred (%)"]
    dmin = row["dept_min (%)"]
    dmax = row["dept_max (%)"]
    with col:
        st.markdown(f"""
<div style="
    background: #fcfcfb;
    border: 1px solid #e1e0d9;
    border-top: 4px solid {color};
    border-radius: 8px;
    padding: 20px 20px 16px;
    text-align: center;
">
  <p style="color: #52514e; font-size: 0.82rem; font-weight: 600;
            letter-spacing: 0.8px; text-transform: uppercase; margin: 0 0 6px;">{label}</p>
  <p style="color: #0b0b0b; font-size: 2.2rem; font-weight: 700; margin: 0 0 4px;">{pred:.1f} %</p>
  <p style="color: #898781; font-size: 0.8rem; margin: 0;">
      Depts : {dmin:.1f} % – {dmax:.1f} %
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Graphique comparatif barres ─────────────────────────────────────────────────
st.markdown("### Comparaison des scénarios")

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
    yaxis=dict(**YAXIS_BASE, ticksuffix=" %", range=[0, 32]),
    xaxis=dict(**XAXIS_BASE, showgrid=False),
    legend=LEGEND_BASE,
    height=340,
)
st.plotly_chart(fig_bar, use_container_width=True)

carte_note(
    "L'écart entre scénarios reste modeste (2,5 pts entre le pire et le meilleur cas), "
    "ce qui reflète la stabilité structurelle de l'abstention : les évolutions lentes de démographie "
    "et d'habitudes électorales contraignent davantage la participation que les conjonctures politiques à court terme."
)

st.markdown("<br>", unsafe_allow_html=True)

# ── Carte prédictions 2027 ───────────────────────────────────────────────────────
st.markdown("### Carte des prédictions 2027 par département")

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
            [0.0, "#cde2fb"],
            [0.5, "#3987e5"],
            [1.0, "#0d366b"],
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
st.markdown("### 🎛️ Simulateur personnalisé")
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
            color_continuous_scale=[[0.0, "#cde2fb"], [0.5, "#3987e5"], [1.0, "#0d366b"]],
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
