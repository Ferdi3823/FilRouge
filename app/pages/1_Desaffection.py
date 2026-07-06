"""
Acte 1 — La désaffection : qui vote encore ?
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.graph_objects as go
from data_loader import load_participation_nationale, load_scores_familles
from _style import inject_css, COULEURS_FAMILLES, PLOTLY_BASE, XAXIS_BASE, YAXIS_BASE, LEGEND_BASE, carte_note, section_title

st.set_page_config(
    page_title="Acte 1 — La désaffection",
    page_icon="🗳️",
    layout="wide",
)
inject_css()

# ── En-tête ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#1c5cab 0%,#2a78d6 100%);
border-radius:10px;padding:28px 32px 22px;margin-bottom:24px;">
  <p style="color:rgba(255,255,255,0.6);font-size:0.72rem;font-weight:700;
  letter-spacing:1.5px;text-transform:uppercase;margin:0 0 6px;">Acte 1 / 3</p>
  <h1 style="color:#fff;font-size:1.7rem;margin:0 0 10px;border:none;">🗳️ La désaffection</h1>
  <p style="color:rgba(255,255,255,0.88);font-size:0.95rem;margin:0;max-width:640px;">
    L'abstention au premier tour a quasiment <strong style="color:#fff;">doublé en 30 ans</strong> :
    de 21&nbsp;% en 1995 à 26&nbsp;% en 2022.
    Dans le même temps, le paysage politique s'est profondément fragmenté.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Données ─────────────────────────────────────────────────────────────────────
df_partic  = load_participation_nationale()
df_familles = load_scores_familles()

t1 = df_partic[df_partic.tour == 1].sort_values("annee")
t2 = df_partic[df_partic.tour == 2].sort_values("annee")

# ── Graphique 1 : courbe d'abstention T1 et T2 ──────────────────────────────────
section_title("Taux d'abstention national (1995–2022)",
              "Agrégation nationale — inscrits, abstentions T1 et T2")

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=t1["annee"], y=t1["taux_abstention"],
    mode="lines+markers",
    name="Tour 1",
    line=dict(color="#2a78d6", width=2.5),
    marker=dict(size=8, color="#2a78d6", line=dict(width=1.5, color="#fcfcfb")),
    hovertemplate="<b>T1 %{x}</b><br>Abstention : %{y:.1f} %<extra></extra>",
))
fig1.add_trace(go.Scatter(
    x=t2["annee"], y=t2["taux_abstention"],
    mode="lines+markers",
    name="Tour 2",
    line=dict(color="#898781", width=2, dash="dot"),
    marker=dict(size=8, color="#898781", line=dict(width=1.5, color="#fcfcfb")),
    hovertemplate="<b>T2 %{x}</b><br>Abstention : %{y:.1f} %<extra></extra>",
))
# Annotation pic 2002
fig1.add_annotation(
    x=2002, y=t1[t1.annee == 2002]["taux_abstention"].values[0],
    text="28,4 % — pic 2002",
    showarrow=True, arrowhead=2, arrowcolor="#52514e", arrowsize=1,
    ax=40, ay=-30, font=dict(color="#52514e", size=11),
)
fig1.update_layout(
    **PLOTLY_BASE,
    yaxis=dict(**YAXIS_BASE, ticksuffix=" %", range=[15, 35]),
    xaxis=dict(**XAXIS_BASE, dtick=5),
    height=340,
    title=dict(text="", x=0),
)
st.plotly_chart(fig1, use_container_width=True)

carte_note(
    "Le pic de 2002 (28,4 %) coïncide avec un premier tour atypique — forte dispersion des voix "
    "entre 16 candidats. La tendance structurelle de hausse reprend à partir de 2012, "
    "indépendamment du format de l'élection."
)

st.markdown("<br>", unsafe_allow_html=True)

# ── Graphique 2 : scores familles T1 ────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
section_title("Part des familles politiques au 1er tour",
              "% des suffrages exprimés — filtrez par famille via le sélecteur")

familles_ordre = [
    "Droite", "Centre", "Gauche", "Extrême droite",
    "Extrême gauche", "Ecologie", "Souverainiste", "Autre",
]
annees = sorted(df_familles["annee"].unique())

tour_filter = st.radio(
    "Filtrer par famille :", ["Toutes"] + familles_ordre,
    horizontal=True, label_visibility="collapsed",
)

fig2 = go.Figure()
for famille in familles_ordre:
    if tour_filter not in ("Toutes", famille):
        continue
    sub = df_familles[df_familles["famille"] == famille].set_index("annee").reindex(annees)
    fig2.add_trace(go.Bar(
        name=famille,
        x=annees,
        y=sub["pct"].values,
        marker_color=COULEURS_FAMILLES.get(famille, "#c3c2b7"),
        marker_line=dict(width=1, color="#fcfcfb"),
        hovertemplate=f"<b>{famille}</b><br>%{{x}} : %{{y:.1f}} %<extra></extra>",
    ))

fig2.update_layout(
    **PLOTLY_BASE,
    barmode="stack",
    yaxis=dict(**YAXIS_BASE, ticksuffix=" %", range=[0, 105]),
    xaxis=dict(**XAXIS_BASE, dtick=1),
    height=380,
    legend=LEGEND_BASE,
)
st.plotly_chart(fig2, use_container_width=True)

carte_note(
    "La montée de l'extrême droite est la tendance longue la plus nette : de 15 % en 1995 à 30 % en 2022. "
    "La gauche traditionnelle (PS + alliés) recule au profit de Mélenchon puis d'un bloc "
    "Gauche/Extrême gauche fragmenté. Le Centre émerge comme famille autonome à partir de 2017 avec Macron."
)
