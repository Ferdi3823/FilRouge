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
  ">Analyse de données · France</p>
  <h1 style="
      color: #ffffff;
      font-size: 2.2rem;
      margin: 0 0 14px;
      border: none;
      letter-spacing: -0.5px;
  ">Élections présidentielles françaises</h1>
  <p style="color: rgba(255,255,255,0.85); font-size: 1.05rem; margin: 0; max-width: 600px;">
      Un demi-siècle de participation, de familles politiques et de démographie —
      du constat (1995–2022) aux scénarios 2027.
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

c1, c2, c3, c4 = st.columns(4)
c1.metric("Élections analysées",  "6",              "1995 → 2022")
c2.metric("Tours de scrutin",     "12",             "T1 + T2")
c3.metric("Départements couverts", str(nb_depts),   "métropole + DOM-TOM")
c4.metric("Abstention T1 2022",   f"{abs_2022:.1f} %", f"+{delta_abs:.1f} pts vs 1995", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ── Cards de navigation ─────────────────────────────────────────────────────────
st.markdown("### Explorez l'analyse en trois actes")
st.markdown("<br>", unsafe_allow_html=True)

card_css = """
<div style="
    background: #fcfcfb;
    border: 1px solid #e1e0d9;
    border-top: 3px solid {color};
    border-radius: 8px;
    padding: 24px 20px 20px;
    height: 100%;
">
  <p style="font-size: 1.4rem; margin: 0 0 8px;">{emoji}</p>
  <h3 style="color: #0b0b0b; font-weight: 600; margin: 0 0 10px; font-size: 1rem;">{titre}</h3>
  <p style="color: #52514e; font-size: 0.88rem; line-height: 1.55; margin: 0;">{desc}</p>
</div>
"""

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown(card_css.format(
        color="#2a78d6", emoji="🗳️",
        titre="Acte 1 — La désaffection",
        desc="L'abstention franchit 30 % au T1 2002, puis repart à la hausse après 2012. "
             "Qui s'est détourné des urnes, et à quelle vitesse ?",
    ), unsafe_allow_html=True)
    st.page_link("pages/1_Desaffection.py", label="Voir l'analyse →", icon="🗳️")

with col2:
    st.markdown(card_css.format(
        color="#1baf7a", emoji="🗺️",
        titre="Acte 2 — Le portrait",
        desc="Les départements d'outre-mer abstiennent à plus de 50 %. "
             "La carte révèle les fractures territoriales, année par année.",
    ), unsafe_allow_html=True)
    st.page_link("pages/2_Portrait.py", label="Voir la carte →", icon="🗺️")

with col3:
    st.markdown(card_css.format(
        color="#eda100", emoji="🔮",
        titre="Acte 3 — Et 2027 ?",
        desc="Le modèle ML projette 24,3 % d'abstention en scénario de base. "
             "Trois hypothèses, trois trajectoires.",
    ), unsafe_allow_html=True)
    st.page_link("pages/3_2027.py", label="Voir les scénarios →", icon="🔮")

# ── Note méthodologique ─────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="color:#898781; font-size:0.8rem; border-top:1px solid #e1e0d9; padding-top:12px;">
Sources : Ministère de l'Intérieur (résultats par département T1 &amp; T2, 1995–2022) ·
INSEE (données démographiques) · Modèle ML : Random Forest entraîné par validation Leave-One-Year-Out.
</div>
""", unsafe_allow_html=True)
