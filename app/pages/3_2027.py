"""
Acte 3 — Et 2027 ? Scénarios de projection.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import urllib.request
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
