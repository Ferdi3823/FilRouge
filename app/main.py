"""
main.py — Page d'accueil.
Lancement : python -X utf8 -m streamlit run app/main.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import streamlit as st
import plotly.graph_objects as go
from data_loader import load_participation_nationale, load_scenarios_2027
from _style import inject_css, PLOTLY_BASE, XAXIS_BASE, YAXIS_BASE

st.set_page_config(
    page_title="Abstention · France 1995–2027",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

st.markdown("""
<style>
@keyframes fadeUp {
  from { opacity:0; transform:translateY(16px); }
  to   { opacity:1; transform:translateY(0); }
}
.anim1 { animation: fadeUp 0.6s ease both; }
.anim2 { animation: fadeUp 0.6s ease 0.15s both; }
.anim3 { animation: fadeUp 0.6s ease 0.30s both; }
.act-card { transition: transform 0.2s ease, box-shadow 0.2s ease; }
.act-card:hover { transform:translateY(-4px); box-shadow:0 12px 28px rgba(0,0,0,0.18) !important; }
</style>
""", unsafe_allow_html=True)

# ── Données ─────────────────────────────────────────────────────────────────────
df_p  = load_participation_nationale()
t1    = df_p[df_p.tour == 1].sort_values("annee")
t2    = df_p[df_p.tour == 2].sort_values("annee")

try:
    df_scen   = load_scenarios_2027()
    pred_base = float(df_scen[df_scen.scenario == "baseline"]["abstention_nationale_pred (%)"].iloc[0])
    pred_max  = float(df_scen["abstention_nationale_pred (%)"].max())
except Exception:
    pred_base, pred_max = 29.3, 30.6

abs_2022 = float(t1[t1.annee == 2022]["taux_abstention"].iloc[0])
abs_1995 = float(t1[t1.annee == 1995]["taux_abstention"].iloc[0])
abs_2002 = float(t1[t1.annee == 2002]["taux_abstention"].iloc[0])
delta    = round(abs_2022 - abs_1995, 1)

# ── Précalcul SVG sparkline ──────────────────────────────────────────────────────
# Données T1 : 1995→2022
spark_data = [21.2, 28.4, 16.2, 20.5, 19.9, 26.3]
spark_years = [1995, 2002, 2007, 2012, 2017, 2022]

def sy(v, vmin=13.0, vmax=30.5, h=72):
    return round(h - (v - vmin) / (vmax - vmin) * h, 1)

spark_pts = [(i * 64, sy(v)) for i, v in enumerate(spark_data)]
spark_line = " ".join(f"{x},{y}" for x, y in spark_pts)
spark_poly = spark_line + " 320,72 0,72"
spark_circles = "".join(
    f'<circle cx="{x}" cy="{y}" r="4" fill="#1e3a6e" stroke="#93c5fd" stroke-width="2"/>'
    for x, y in spark_pts
)
spark_labels = "".join(
    f'<text x="{x}" y="82" fill="rgba(255,255,255,0.35)" font-size="9" text-anchor="middle">{yr}</text>'
    for (x, _), yr in zip(spark_pts, spark_years)
)
y2027 = sy(pred_base)

# ── HERO — deux colonnes ─────────────────────────────────────────────────────────
col_txt, col_spark = st.columns([3, 2], gap="large")

with col_txt:
    st.markdown(f"""
<div style="background:linear-gradient(135deg,#080f1c 0%,#0d1b35 60%,#112244 100%);
border-radius:14px;padding:44px 40px 36px;min-height:300px;">
  <p class="anim1" style="color:rgba(255,255,255,0.4);font-size:0.65rem;font-weight:700;
    letter-spacing:2.5px;text-transform:uppercase;margin:0 0 18px;">
    Analyse · France · 1995 – 2027
  </p>
  <h1 class="anim1" style="color:#fff;font-size:2.6rem;font-weight:800;line-height:1.1;
    margin:0 0 6px;letter-spacing:-1px;border:none;">
    L'abstention&nbsp;—
  </h1>
  <h1 class="anim2" style="color:#fff;font-size:2.6rem;font-weight:800;line-height:1.1;
    margin:0 0 22px;letter-spacing:-1px;border:none;">
    trente ans de silence
  </h1>
  <p class="anim2" style="color:rgba(255,255,255,0.72);font-size:0.97rem;
    margin:0 0 28px;max-width:440px;line-height:1.65;">
    En 1995, <strong style="color:#fff;">1 Français sur 5</strong> ne votait pas au T1.
    En 2022, c'est <strong style="color:#fff;">1 sur 4</strong>.
    Ce projet retrace le désengagement, cartographie ses causes,
    et projette ce que 2027 pourrait réserver.
  </p>
  <div class="anim3" style="display:flex;gap:16px;flex-wrap:wrap;">
    <div style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.14);
      border-radius:8px;padding:12px 16px;">
      <p style="color:#7ab8f5;font-size:1.45rem;font-weight:700;margin:0;line-height:1;">{abs_2022:.1f}%</p>
      <p style="color:rgba(255,255,255,0.45);font-size:0.7rem;margin:3px 0 0;">abstention T1 2022</p>
    </div>
    <div style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.14);
      border-radius:8px;padding:12px 16px;">
      <p style="color:#fbbf24;font-size:1.45rem;font-weight:700;margin:0;line-height:1;">{abs_2002:.1f}%</p>
      <p style="color:rgba(255,255,255,0.45);font-size:0.7rem;margin:3px 0 0;">pic historique 2002</p>
    </div>
    <div style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.14);
      border-radius:8px;padding:12px 16px;">
      <p style="color:#34d399;font-size:1.45rem;font-weight:700;margin:0;line-height:1;">~{pred_base:.0f}%</p>
      <p style="color:rgba(255,255,255,0.45);font-size:0.7rem;margin:3px 0 0;">prédit 2027</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

with col_spark:
    st.markdown(f"""
<div style="background:linear-gradient(135deg,#080f1c 0%,#0d1b35 100%);
border-radius:14px;padding:28px 24px 20px;height:100%;display:flex;
flex-direction:column;justify-content:center;">
  <p style="color:rgba(255,255,255,0.35);font-size:0.63rem;font-weight:700;
    letter-spacing:1.5px;text-transform:uppercase;margin:0 0 16px;">
    Abstention T1 · 1995 – 2027
  </p>
  <svg viewBox="0 0 340 88" width="100%" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.35"/>
        <stop offset="100%" stop-color="#3b82f6" stop-opacity="0.02"/>
      </linearGradient>
    </defs>
    <polygon points="{spark_poly}" fill="url(#sg)"/>
    <polyline points="{spark_line}" fill="none" stroke="#60a5fa"
      stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>
    {spark_circles}
    {spark_labels}
    <line x1="320" y1="{spark_pts[-1][1]}" x2="336" y2="{y2027}"
      stroke="#f59e0b" stroke-width="1.8" stroke-dasharray="4 3"/>
    <circle cx="336" cy="{y2027}" r="5" fill="#f59e0b" stroke="#fff" stroke-width="1.5"/>
    <text x="336" y="{y2027 - 9}" fill="#fbbf24" font-size="9"
      text-anchor="middle" font-weight="bold">2027?</text>
  </svg>
  <p style="color:rgba(255,255,255,0.25);font-size:0.68rem;margin:10px 0 0;text-align:center;">
    Point ambre = projection modèle
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── 3 CHIFFRES CHOCS ────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3, gap="small")

c1.markdown(f"""
<div style="background:#fff;border:1px solid #e1e0d9;border-top:4px solid #c0392b;
border-radius:10px;padding:24px 22px;">
  <p style="color:#898781;font-size:0.65rem;font-weight:700;letter-spacing:1.5px;
  text-transform:uppercase;margin:0 0 10px;">Tendance 1995 → 2022</p>
  <p style="color:#c0392b;font-size:3rem;font-weight:800;line-height:1;
  margin:0 0 6px;letter-spacing:-2px;">+{delta}<span style="font-size:1.4rem;"> pp</span></p>
  <p style="color:#52514e;font-size:0.85rem;line-height:1.55;margin:0;">
    De <strong>{abs_1995:.1f}%</strong> à <strong>{abs_2022:.1f}%</strong> —
    une hausse structurelle sur trente ans, indépendante des candidats.
  </p>
</div>
""", unsafe_allow_html=True)

c2.markdown(f"""
<div style="background:#fff;border:1px solid #e1e0d9;border-top:4px solid #1a2c50;
border-radius:10px;padding:24px 22px;">
  <p style="color:#898781;font-size:0.65rem;font-weight:700;letter-spacing:1.5px;
  text-transform:uppercase;margin:0 0 10px;">Ampleur du phénomène</p>
  <p style="color:#1a2c50;font-size:3rem;font-weight:800;line-height:1;
  margin:0 0 6px;letter-spacing:-2px;">1<span style="font-size:1.4rem;"> / </span>4</p>
  <p style="color:#52514e;font-size:0.85rem;line-height:1.55;margin:0;">
    Au T1 2022, <strong>1 Français inscrit sur 4</strong> n'a pas voté.
    En 2002, le pic atteignait <strong>{abs_2002:.1f}%</strong>.
  </p>
</div>
""", unsafe_allow_html=True)

c3.markdown(f"""
<div style="background:#fff;border:1px solid #e1e0d9;border-top:4px solid #a05800;
border-radius:10px;padding:24px 22px;">
  <p style="color:#898781;font-size:0.65rem;font-weight:700;letter-spacing:1.5px;
  text-transform:uppercase;margin:0 0 10px;">Projection T1 2027</p>
  <p style="color:#a05800;font-size:3rem;font-weight:800;line-height:1;
  margin:0 0 6px;letter-spacing:-2px;">{pred_base:.0f}<span style="font-size:1.4rem;">%</span></p>
  <p style="color:#52514e;font-size:0.85rem;line-height:1.55;margin:0;">
    Scénario de base Ridge — fourchette
    <strong>26 – {pred_max:.0f}%</strong>
    selon les scénarios, données législatives 2017 &amp; 2022 intégrées.
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── GRAPHIQUE TENDANCE ───────────────────────────────────────────────────────────
annees = t1["annee"].values.astype(float)
vals   = t1["taux_abstention"].values
x_fit  = annees[annees >= 2007]
y_fit  = vals[annees >= 2007]
slope, intercept = np.polyfit(x_fit, y_fit, 1)
x_ext = np.linspace(2007, 2028, 150)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=[2027, 2027], y=[22.1, 34.2],
    mode="lines", line=dict(color="#eda100", width=18),
    opacity=0.12, showlegend=False, hoverinfo="skip",
))
fig.add_trace(go.Scatter(
    x=x_ext, y=intercept + slope * x_ext,
    mode="lines", name="Tendance 2007–2022",
    line=dict(color="#2a78d6", width=1.5, dash="dash"),
    opacity=0.55, hoverinfo="skip",
))
fig.add_trace(go.Scatter(
    x=t2["annee"], y=t2["taux_abstention"],
    mode="lines+markers", name="Tour 2",
    line=dict(color="#c3c2b7", width=1.8, dash="dot"),
    marker=dict(size=7, color="#c3c2b7"),
    hovertemplate="<b>T2 %{x}</b> — %{y:.1f}%<extra></extra>",
))
fig.add_trace(go.Scatter(
    x=t1["annee"], y=t1["taux_abstention"],
    mode="lines+markers", name="Tour 1",
    line=dict(color="#2a78d6", width=3),
    marker=dict(size=10, color="#2a78d6", line=dict(width=2.5, color="#fff")),
    hovertemplate="<b>T1 %{x}</b> — %{y:.1f}%<extra></extra>",
))
fig.add_annotation(
    x=2002, y=abs_2002,
    text=f"Pic 2002 : {abs_2002:.1f}%",
    showarrow=True, arrowhead=2, arrowcolor="#52514e",
    ax=50, ay=-32, font=dict(color="#52514e", size=11, family="Inter"),
)
fig.add_trace(go.Scatter(
    x=[2027], y=[pred_base],
    mode="markers", name=f"Préd. 2027 (~{pred_base:.0f}%)",
    marker=dict(size=16, color="#eda100", symbol="star",
                line=dict(width=2, color="#fff")),
    hovertemplate=f"<b>Projection 2027</b><br>Scénario de base : {pred_base:.1f}%<extra></extra>",
))
fig.add_vline(x=2022.5, line_dash="dot", line_color="#d0cfc8", line_width=1.2,
              annotation_text="projection →",
              annotation_position="top right",
              annotation_font=dict(color="#898781", size=10))
fig.update_layout(
    **PLOTLY_BASE,
    title=dict(
        text="<b>Abstention T1 et T2 · 1995–2022 + projection 2027</b>",
        font=dict(size=13, color="#0d0d0d"), x=0,
    ),
    yaxis=dict(**YAXIS_BASE, ticksuffix=" %", range=[10, 38],
               title="Taux d'abstention (%)"),
    xaxis=dict(**XAXIS_BASE, range=[1993, 2030], dtick=5),
    height=340,
    legend=dict(orientation="h", yanchor="bottom", y=1.02,
                xanchor="left", x=0, font=dict(size=11, color="#52514e"),
                bgcolor="rgba(0,0,0,0)"),
)
st.plotly_chart(fig, use_container_width=True)

# ── SÉPARATEUR ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:16px;margin:28px 0 24px;">
  <div style="flex:1;height:1px;background:#e1e0d9;"></div>
  <p style="color:#c3c2b7;font-size:0.65rem;font-weight:700;letter-spacing:2.5px;
    text-transform:uppercase;margin:0;white-space:nowrap;">L'analyse en trois actes</p>
  <div style="flex:1;height:1px;background:#e1e0d9;"></div>
</div>
""", unsafe_allow_html=True)

# ── 3 ACTES ──────────────────────────────────────────────────────────────────────
ACTES = [
    {
        "num": "01", "page": "pages/1_Desaffection.py",
        "bg": "linear-gradient(150deg,#0f2952 0%,#1c4a8a 100%)",
        "accent": "#7ab8f5", "emoji": "🗳️",
        "titre": "La désaffection",
        "hook": "Que s'est-il passé ?",
        "stat": f"+{delta} pp", "stat_label": "depuis 1995",
        "desc": "L'abstention a quasiment doublé en 30 ans. La carte politique se recompose : extrême droite 15% → 30%, émergence du Centre avec Macron.",
    },
    {
        "num": "02", "page": "pages/2_Portrait.py",
        "bg": "linear-gradient(150deg,#0a3322 0%,#125c3c 100%)",
        "accent": "#6ee7b7", "emoji": "🗺️",
        "titre": "Le portrait",
        "hook": "Qui abstient, et où ?",
        "stat": "r = 0.41", "stat_label": "chômage × abstention",
        "desc": "4 profils de territoires par clustering. Les \"territoires décrochés\" : 32% d'abstention moyenne. Le chômage est le prédicteur le plus fort.",
    },
    {
        "num": "03", "page": "pages/3_2027.py",
        "bg": "linear-gradient(150deg,#5c3100 0%,#a05800 100%)",
        "accent": "#fcd34d", "emoji": "🔮",
        "titre": "Et 2027 ?",
        "hook": "Que peut-on projeter ?",
        "stat": f"~{pred_base:.0f}%", "stat_label": "scénario de base",
        "desc": "Deux méthodes + 4 scénarios dont « 2027 sans Macron ». Sondages d'intention intégrés. Simulateur interactif temps réel.",
    },
]

ca, cb, cc = st.columns(3, gap="large")
for col, a in zip([ca, cb, cc], ACTES):
    with col:
        st.markdown(f"""
<div class="act-card" style="background:{a['bg']};border-radius:12px;
padding:30px 24px 24px;box-shadow:0 4px 16px rgba(0,0,0,0.14);position:relative;overflow:hidden;">
  <p style="position:absolute;top:-14px;right:12px;font-size:5.5rem;font-weight:900;
    color:rgba(255,255,255,0.05);margin:0;line-height:1;user-select:none;">{a['num']}</p>
  <p style="color:rgba(255,255,255,0.4);font-size:0.62rem;font-weight:700;
    letter-spacing:2px;text-transform:uppercase;margin:0 0 8px;">Acte {a['num']}</p>
  <p style="font-size:1.7rem;margin:0 0 4px;">{a['emoji']}</p>
  <h3 style="color:#fff;font-size:1.15rem;font-weight:700;margin:0 0 4px;">{a['titre']}</h3>
  <p style="color:{a['accent']};font-size:0.8rem;font-style:italic;margin:0 0 14px;">{a['hook']}</p>
  <div style="background:rgba(0,0,0,0.22);border-radius:8px;padding:12px 14px;margin-bottom:14px;">
    <p style="color:{a['accent']};font-size:1.9rem;font-weight:800;margin:0;line-height:1;">{a['stat']}</p>
    <p style="color:rgba(255,255,255,0.5);font-size:0.68rem;margin:2px 0 0;">{a['stat_label']}</p>
  </div>
  <p style="color:rgba(255,255,255,0.72);font-size:0.81rem;line-height:1.6;margin:0 0 18px;">{a['desc']}</p>
</div>
""", unsafe_allow_html=True)
        st.page_link(a["page"], label=f"Ouvrir l'acte {a['num']} →", icon=a["emoji"])

# ── FOOTER ───────────────────────────────────────────────────────────────────────
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="border-top:1px solid #e1e0d9;padding-top:14px;
  display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px;">
  <p style="color:#c3c2b7;font-size:0.75rem;margin:0;line-height:1.6;">
    <strong style="color:#a0a09a;">Sources :</strong>
    Ministère de l'Intérieur (data.gouv.fr) · INSEE population 1975–2024 ·
    INSEE chômage 2022 · Filosofi revenus 2021 · Législatives 2017 &amp; 2022
  </p>
  <p style="color:#c3c2b7;font-size:0.75rem;margin:0;line-height:1.6;">
    <strong style="color:#a0a09a;">Modèles :</strong>
    Ridge · LOYO CV · KMeans · Régression linéaire + IC
  </p>
</div>
""", unsafe_allow_html=True)
