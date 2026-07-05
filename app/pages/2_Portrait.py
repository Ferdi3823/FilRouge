"""
Acte 2 — Le portrait des abstentionnistes.
Carte choroplèthe de l'abstention par département.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import urllib.request
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data_loader import load_demography, load_dept_clusters
from _style import inject_css, PLOTLY_BASE, XAXIS_BASE, YAXIS_BASE, carte_note

st.set_page_config(
    page_title="Acte 2 — Le portrait",
    page_icon="🗺️",
    layout="wide",
)
inject_css()

# ── GeoJSON départements français ────────────────────────────────────────────────
GEO_URL = (
    "https://raw.githubusercontent.com/gregoiredavid/"
    "france-geojson/master/departements-version-simplifiee.geojson"
)

@st.cache_data(ttl=3600)
def load_geojson():
    with urllib.request.urlopen(GEO_URL) as r:
        return json.loads(r.read().decode())


# ── Données ─────────────────────────────────────────────────────────────────────
@st.cache_data
def build_map_data():
    df = load_demography()
    # Tour 1 uniquement, departements metropole + DOM (codes courts)
    t1 = df[df.tour == 1].copy()
    t1["dept_code"] = t1["dept_code"].astype(str).str.zfill(2)
    return t1

df_map   = build_map_data()
df_clust = load_dept_clusters()
df_clust["dept_code"] = df_clust["dept_code"].astype(str).str.zfill(2)

annees = sorted(df_map["annee"].unique())

# ── En-tête ─────────────────────────────────────────────────────────────────────
st.markdown("## 🗺️ Acte 2 — Le portrait des abstentionnistes")
st.markdown(
    "Derrière la moyenne nationale se cachent des réalités très différentes. "
    "Les **DOM-TOM abstiennent deux fois plus** que la métropole. "
    "Les départements les plus jeunes — souvent les plus précaires — décrochent les premiers."
)
st.markdown("<br>", unsafe_allow_html=True)

# ── Contrôles ───────────────────────────────────────────────────────────────────
col_ctrl, _ = st.columns([2, 3])
with col_ctrl:
    annee_choisie = st.select_slider(
        "Année de l'élection",
        options=annees,
        value=2022,
    )

# ── Filtre ──────────────────────────────────────────────────────────────────────
df_annee = df_map[df_map.annee == annee_choisie][
    ["dept_code", "dept_nom_election", "taux_abstention", "pct_jeunes", "pct_seniors"]
].drop_duplicates("dept_code")

# ── Métriques résumées ──────────────────────────────────────────────────────────
metro_mask = df_annee["dept_code"].str.len() <= 2
abs_metro  = df_annee[metro_mask]["taux_abstention"].mean()
abs_domtom = df_annee[~metro_mask]["taux_abstention"].mean()
abs_nat    = df_annee["taux_abstention"].mean()

m1, m2, m3 = st.columns(3)
m1.metric("Abstention nationale (moy. depts)", f"{abs_nat:.1f} %")
m2.metric("Métropole",  f"{abs_metro:.1f} %")
m3.metric("DOM-TOM",    f"{abs_domtom:.1f} %",
          f"+{abs_domtom - abs_metro:.1f} pts vs métropole", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)

# ── Carte ────────────────────────────────────────────────────────────────────────
st.markdown(f"### Taux d'abstention T1 {annee_choisie} par département")

try:
    geojson = load_geojson()
    fig_map = px.choropleth(
        df_annee,
        geojson=geojson,
        locations="dept_code",
        featureidkey="properties.code",
        color="taux_abstention",
        hover_name="dept_nom_election",
        hover_data={"taux_abstention": ":.1f", "dept_code": False},
        color_continuous_scale=[
            [0.0, "#cde2fb"],
            [0.4, "#3987e5"],
            [0.7, "#256abf"],
            [1.0, "#0d366b"],
        ],
        range_color=[10, 70],
        labels={"taux_abstention": "Abstention (%)"},
    )
    fig_map.update_geos(
        fitbounds="locations", visible=False,
        bgcolor="#f5f4f2",
    )
    fig_map.update_layout(
        paper_bgcolor="#f5f4f2",
        margin=dict(l=0, r=0, t=0, b=0),
        height=500,
        coloraxis_colorbar=dict(
            title="Abstention (%)",
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
    st.warning(f"Carte non disponible (vérifier la connexion internet) : {e}")
    st.dataframe(df_annee.sort_values("taux_abstention", ascending=False).head(15))

carte_note(
    "La couleur bleue foncée indique une abstention élevée. Les DOM-TOM (Guyane, Mayotte…) "
    "atteignent régulièrement 50–70 %, un phénomène structurel lié à l'éloignement géographique, "
    "à la jeunesse de la population et à la faible confiance institutionnelle."
)

st.markdown("<br>", unsafe_allow_html=True)

# ── Graphique : top / flop départements ─────────────────────────────────────────
st.markdown(f"### Les 10 départements les plus et les moins abstentionnistes en {annee_choisie}")

df_sorted = df_annee.sort_values("taux_abstention")
top10  = df_sorted.tail(10)
flop10 = df_sorted.head(10)
df_bar = pd.concat([flop10, top10])

col_colors = [
    "#2a78d6" if v < df_annee["taux_abstention"].median() else "#e34948"
    for v in df_bar["taux_abstention"]
]

fig_bar = go.Figure(go.Bar(
    x=df_bar["taux_abstention"],
    y=df_bar["dept_nom_election"],
    orientation="h",
    marker_color=col_colors,
    marker_line=dict(width=0),
    hovertemplate="<b>%{y}</b><br>Abstention : %{x:.1f} %<extra></extra>",
))
fig_bar.update_layout(
    **PLOTLY_BASE,
    xaxis=dict(**XAXIS_BASE, ticksuffix=" %", range=[0, 75]),
    yaxis=dict(**YAXIS_BASE),
    height=420,
    showlegend=False,
)
st.plotly_chart(fig_bar, use_container_width=True)
