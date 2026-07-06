"""
main.py — Page d'accueil.
Lancement : streamlit run app/main.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from data_loader import load_participation_nationale, load_demography
from _style import inject_css

st.set_page_config(
    page_title="Présidentielles françaises 1995–2027",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

# ── Hero ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(135deg, #1c5cab 0%, #2a78d6 60%, #3987e5 100%);
    border-radius: 12px;
    padding: 48px 40px 36px;
    margin-bottom: 32px;
">
  <p style="
      color: rgba(255,255,255,0.70);
      font-size: 12px;
      font-weight: 600;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      margin: 0 0 10px;
  ">Analyse de données · France · 1995 – 2027</p>
  <h1 style="
      color: #ffffff;
      font-size: 2.2rem;
      margin: 0 0 14px;
      border: none;
      letter-spacing: -0.5px;
  ">Élections présidentielles françaises</h1>
  <p style="color: rgba(255,255,255,0.90); font-size: 1.05rem; margin: 0 0 10px; max-width: 680px;">
      En 27 ans, un Français sur quatre s'est détourné des urnes au premier tour.
      Cette analyse retrace la montée de l'abstention depuis 1995, identifie ses déterminants
      — démographiques, territoriaux, socio-économiques — et projette ce que 2027 pourrait réserver.
  </p>
  <p style="color: rgba(255,255,255,0.65); font-size: 0.85rem; margin: 0;">
      6 élections · 96–100 départements · 7 000 résultats de candidats · modèle Ridge + régression linéaire
  </p>
</div>
""", unsafe_allow_html=True)

# ── Métriques clés ──────────────────────────────────────────────────────────────
df_partic = load_participation_nationale()
df_demo   = load_demography()

abs_1995  = df_partic[(df_partic.annee == 1995) & (df_partic.tour == 1)]["taux_abstention"].values[0]
abs_2022  = df_partic[(df_partic.annee == 2022) & (df_partic.tour == 1)]["taux_abstention"].values[0]
delta_abs = abs_2022 - abs_1995
nb_depts  = df_demo["dept_code"].nunique()
nb_candidats = 0
try:
    import pandas as pd
    BASE_DIR = Path(__file__).resolve().parent.parent
    df_cand = pd.read_csv(BASE_DIR / "outputs" / "elections_candidats.csv")
    nb_candidats = df_cand["candidat"].nunique()
except Exception:
    nb_candidats = 64

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Élections analysées",   "6",                  "1995 → 2022")
c2.metric("Candidats uniques",     str(nb_candidats),    "T1, toutes années")
c3.metric("Départements couverts", str(nb_depts),        "métropole + DOM-TOM")
c4.metric("Abstention T1 2022",    f"{abs_2022:.1f} %",  f"+{delta_abs:.1f} pts vs 1995",
          delta_color="inverse")
c5.metric("Prédiction 2027 (T1)",  "~29 %",              "fourchette : 24–34 %", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ── Histoire en 3 actes ──────────────────────────────────────────────────────────
st.markdown("### L'histoire en trois actes")
st.markdown(
    "Cette analyse suit un fil narratif en trois temps. "
    "Chaque acte répond à une question précise, s'appuie sur les précédents et ouvre vers le suivant."
)
st.markdown("<br>", unsafe_allow_html=True)

card_css = """
<div style="
    background: #fcfcfb;
    border: 1px solid #e1e0d9;
    border-left: 5px solid {color};
    border-radius: 8px;
    padding: 24px 20px 20px;
    height: 100%;
">
  <p style="font-size: 0.72rem; color:#898781; font-weight:600;
            letter-spacing:1.2px; text-transform:uppercase; margin:0 0 6px;">Acte {num}</p>
  <p style="font-size: 1.4rem; margin: 0 0 6px;">{emoji}</p>
  <h3 style="color: #0b0b0b; font-weight: 700; margin: 0 0 8px; font-size: 1rem;">{titre}</h3>
  <p style="color: #52514e; font-size: 0.88rem; line-height: 1.6; margin: 0 0 10px;">{question}</p>
  <p style="color: #898781; font-size: 0.80rem; line-height: 1.5; margin: 0;">{contenu}</p>
</div>
"""

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown(card_css.format(
        color="#2a78d6", num="1", emoji="🗳️",
        titre="La désaffection",
        question="<strong>Que s'est-il passé ?</strong> Comment l'abstention a-t-elle évolué depuis 1995 ?",
        contenu="Courbe de participation T1 et T2 · Recomposition des familles politiques · "
                "Montée de l'extrême droite (15% → 30%) · Émergence du Centre avec Macron.",
    ), unsafe_allow_html=True)
    st.page_link("pages/1_Desaffection.py", label="Voir l'acte 1 →", icon="🗳️")

with col2:
    st.markdown(card_css.format(
        color="#1baf7a", num="2", emoji="🗺️",
        titre="Le portrait",
        question="<strong>Qui abstient, et où ?</strong> Les inégalités territoriales et sociales.",
        contenu="Carte interactive 1995–2022 · 4 profils de territoires (clustering) · "
                "Chômage et revenus médians : les vrais déterminants (r=+0.41 pour le chômage).",
    ), unsafe_allow_html=True)
    st.page_link("pages/2_Portrait.py", label="Voir l'acte 2 →", icon="🗺️")

with col3:
    st.markdown(card_css.format(
        color="#eda100", num="3", emoji="🔮",
        titre="Et 2027 ?",
        question="<strong>Que peut-on projeter ?</strong> Deux méthodes, des fourchettes honnêtes.",
        contenu="Régression linéaire avec IC (méthode transparente) · "
                "3 scénarios Ridge par département · Simulateur interactif (sliders temps réel).",
    ), unsafe_allow_html=True)
    st.page_link("pages/3_2027.py", label="Voir l'acte 3 →", icon="🔮")

st.markdown("<br>", unsafe_allow_html=True)

# ── Note narrative ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    background:#f8f8f6; border-left:3px solid #2a78d6;
    border-radius:4px; padding:16px 20px; margin-bottom:24px;
">
  <p style="color:#52514e; font-size:0.88rem; margin:0; line-height:1.6;">
    <strong>Pourquoi trois actes ?</strong>
    La compréhension de l'abstention nécessite de passer du <em>quoi</em> (tendances historiques)
    au <em>qui</em> (profils territoriaux et sociaux) avant d'aborder le <em>et alors</em>
    (projections). Lire les actes dans l'ordre donne la cohérence narrative maximale —
    mais chaque acte se lit aussi indépendamment.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Note méthodologique ─────────────────────────────────────────────────────────
st.markdown("""
<div style="color:#898781; font-size:0.80rem; border-top:1px solid #e1e0d9; padding-top:12px;">
<strong>Sources :</strong>
Ministère de l'Intérieur — résultats par département T1 &amp; T2, 1995–2022 (data.gouv.fr) ·
INSEE — estimations de population par département et groupe d'âge (1975–2024) ·
INSEE — taux de chômage localisés 2022 · INSEE Filosofi — revenus médians 2021.
<br>
<strong>Modèles :</strong>
Régression linéaire + IC (scipy.stats.t) · Ridge pipeline (scikit-learn, validation Leave-One-Year-Out).
</div>
""", unsafe_allow_html=True)
