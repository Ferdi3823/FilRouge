"""
Acte 2 — Le portrait des abstentionnistes.
Carte choroplèthe de l'abstention par département.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import urllib.request
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data_loader import load_demography, load_dept_clusters
from _style import inject_css, PLOTLY_BASE, XAXIS_BASE, YAXIS_BASE, carte_note, section_title

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TABLE_DIR = BASE_DIR / "outputs" / "tables"

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
st.markdown("""
<div style="background:linear-gradient(135deg,#0e7a5a 0%,#1baf7a 100%);
border-radius:10px;padding:28px 32px 22px;margin-bottom:24px;">
  <p style="color:rgba(255,255,255,0.6);font-size:0.72rem;font-weight:700;
  letter-spacing:1.5px;text-transform:uppercase;margin:0 0 6px;">Acte 2 / 3</p>
  <h1 style="color:#fff;font-size:1.7rem;margin:0 0 10px;border:none;">🗺️ Le portrait</h1>
  <p style="color:rgba(255,255,255,0.88);font-size:0.95rem;margin:0;max-width:640px;">
    Derrière la moyenne nationale se cachent des réalités très différentes.
    Les DOM-TOM abstiennent <strong style="color:#fff;">deux fois plus</strong> que la métropole.
    Le chômage est le déterminant le plus fort — plus que la démographie.
  </p>
</div>
""", unsafe_allow_html=True)

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
section_title(f"Taux d'abstention T1 {annee_choisie} par département",
              "Cliquez sur un département pour le détail · Couleur = niveau d'abstention")

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
section_title(f"Palmarès {annee_choisie}",
              "10 départements les plus abstentionnistes (rouge) vs les moins (bleu)")

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

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# ── Profils de territoires (clustering) ──────────────────────────────────────
st.markdown("### 🗂️ Les 4 profils de territoires")
st.markdown(
    "Un algorithme de clustering (KMeans) identifie **4 familles de départements** "
    "aux comportements électoraux homogènes, en métropole uniquement. "
    "Ces profils permettent de comprendre *qui* abstient et *pourquoi*, au-delà des moyennes."
)

# Noms et descriptions des clusters (basés sur les profils calculés par build_features.py)
CLUSTER_NAMES = {
    0: ("🏭 Bastions populaires",     "#e74c3c",
        "Forte extrême droite (~20%), peu de seniors. "
        "Abstention moyenne (~21%). Départements industriels en transition."),
    1: ("🌾 Vieux terroirs socialistes", "#2980b9",
        "Forte gauche traditionnelle (~31%), très seniors (~30%). "
        "Abstention la plus basse (~19%). Histoire électorale ancrée à gauche."),
    2: ("📉 Territoires décrochés",   "#7f8c8d",
        "Abstention très élevée (~32%), peu de vote Centre. "
        "Profil précaire, souvent périphérique ou rural profond."),
    3: ("🏙️ Métropoles dynamiques",   "#27ae60",
        "Population très jeune (~55%), fort vote Centre+Gauche. "
        "Abstention modérée (~22%). Grandes agglomérations."),
}

try:
    df_clust_full = load_dept_clusters()
    df_clust_full["dept_code"] = df_clust_full["dept_code"].astype(str).str.zfill(2)

    # 4 cartes de profil
    cols_clust = st.columns(4, gap="small")
    for i, (col, (k, (name, color, desc))) in enumerate(
        zip(cols_clust, CLUSTER_NAMES.items())
    ):
        depts = df_clust_full[df_clust_full["cluster"] == k]["dept_nom"]
        n = len(depts)
        with col:
            st.markdown(f"""
<div style="
    background:#fcfcfb; border:1px solid #e1e0d9;
    border-top:4px solid {color}; border-radius:8px;
    padding:16px 14px 14px; height:210px; overflow:hidden;
">
  <p style="color:#0b0b0b;font-size:0.95rem;font-weight:700;margin:0 0 6px;">{name}</p>
  <p style="color:#52514e;font-size:0.78rem;margin:0 0 8px;">{desc}</p>
  <p style="color:#898781;font-size:0.75rem;margin:0;"><em>{n} département{'s' if n>1 else ''}</em></p>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tableau des départements par cluster
    with st.expander("Voir la liste complète des départements par profil"):
        for k, (name, color, _) in CLUSTER_NAMES.items():
            depts_k = df_clust_full[df_clust_full["cluster"] == k]["dept_nom"].sort_values()
            st.markdown(f"**{name}** ({len(depts_k)} depts)")
            st.write(", ".join(depts_k.tolist()))

except Exception as e:
    st.info(f"Clustering non disponible : {e}. Lancez `python src/build_features.py`.")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# ── Analyse socio-économique ─────────────────────────────────────────────────
st.markdown("### 💼 Chômage et revenus : les déterminants structurels")
st.markdown(
    "La corrélation démographie × abstention (r ≈ 0.38 pour les jeunes) "
    "est renforcée quand on ajoute les inégalités économiques. "
    "Le **taux de chômage** est le prédicteur le plus fort (r = +0.41 en 2022)."
)

try:
    df_socio = pd.read_csv(TABLE_DIR / "socioeco_dept.csv")
    df_2022 = df_map[df_map.annee == 2022].copy()
    df_2022 = df_2022[df_2022["dept_code"].str.len() <= 2].drop_duplicates("dept_code")
    df_merged = df_2022.merge(df_socio, on="dept_code", how="inner")

    tab1, tab2 = st.tabs(["Chômage vs Abstention", "Revenus vs Abstention"])

    with tab1:
        r_chom = df_merged["taux_chomage_2022"].corr(df_merged["taux_abstention"])
        z = np.polyfit(df_merged["taux_chomage_2022"], df_merged["taux_abstention"], 1)
        xs = np.linspace(df_merged["taux_chomage_2022"].min(),
                         df_merged["taux_chomage_2022"].max(), 100)

        fig_c = go.Figure()
        fig_c.add_trace(go.Scatter(
            x=df_merged["taux_chomage_2022"],
            y=df_merged["taux_abstention"],
            mode="markers",
            marker=dict(size=9, color="#e74c3c", opacity=0.7),
            text=df_merged["dept_nom_election"],
            hovertemplate="<b>%{text}</b><br>Chômage : %{x:.1f}%<br>Abstention : %{y:.1f}%<extra></extra>",
        ))
        fig_c.add_trace(go.Scatter(
            x=xs, y=np.poly1d(z)(xs),
            mode="lines",
            line=dict(color="#c0392b", width=2, dash="dash"),
            name=f"Tendance (r={r_chom:+.2f})",
        ))
        fig_c.update_layout(
            **PLOTLY_BASE,
            xaxis=dict(**XAXIS_BASE, title="Taux de chômage 2022 (%)", ticksuffix="%"),
            yaxis=dict(**YAXIS_BASE, title="Taux d'abstention T1 2022 (%)", ticksuffix="%"),
            height=380,
            showlegend=True,
        )
        st.plotly_chart(fig_c, use_container_width=True)
        carte_note(
            f"Corrélation chômage × abstention : r = {r_chom:+.2f}. "
            "Les Pyrénées-Orientales (13.4%), l'Hérault (12.1%) et la Seine-Saint-Denis (12.0%) "
            "cumulent chômage élevé et forte abstention. "
            "À l'opposé, l'Ain, la Mayenne et la Vendée combinent plein emploi et forte participation."
        )

    with tab2:
        r_rev = df_merged["revenu_median_2021"].corr(df_merged["taux_abstention"])
        z2 = np.polyfit(df_merged["revenu_median_2021"], df_merged["taux_abstention"], 1)
        xs2 = np.linspace(df_merged["revenu_median_2021"].min(),
                          df_merged["revenu_median_2021"].max(), 100)

        fig_r = go.Figure()
        fig_r.add_trace(go.Scatter(
            x=df_merged["revenu_median_2021"],
            y=df_merged["taux_abstention"],
            mode="markers",
            marker=dict(size=9, color="#2980b9", opacity=0.7),
            text=df_merged["dept_nom_election"],
            hovertemplate="<b>%{text}</b><br>Revenu médian : %{x:,.0f} €<br>Abstention : %{y:.1f}%<extra></extra>",
        ))
        fig_r.add_trace(go.Scatter(
            x=xs2, y=np.poly1d(z2)(xs2),
            mode="lines",
            line=dict(color="#1a5276", width=2, dash="dash"),
            name=f"Tendance (r={r_rev:+.2f})",
        ))
        fig_r.update_layout(
            **PLOTLY_BASE,
            xaxis=dict(**XAXIS_BASE, title="Revenu médian 2021 (€/UC)"),
            yaxis=dict(**YAXIS_BASE, title="Taux d'abstention T1 2022 (%)", ticksuffix="%"),
            height=380,
            showlegend=True,
        )
        st.plotly_chart(fig_r, use_container_width=True)
        carte_note(
            f"Corrélation revenu médian × abstention : r = {r_rev:+.2f}. "
            "La relation est plus faible que pour le chômage, ce qui suggère que "
            "l'insécurité de l'emploi (chômage) pèse davantage sur l'abstention que le niveau de revenus en soi. "
            "Paris et les Hauts-de-Seine, très riches, abstiennent autant que la moyenne."
        )

except Exception as e:
    st.info(f"Données socio-économiques non disponibles ({e}). Lancez `python src/merge_socioeco.py`.")
