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

# ── CSS additionnel pour la home ────────────────────────────────────────────────
st.markdown("""
<style>
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}
.hero-num   { animation: fadeUp 0.7s ease both; }
.hero-sub   { animation: fadeUp 0.9s ease both; }
.stat-card  { animation: fadeUp 1.1s ease both; }
.act-card   { transition: transform 0.2s ease, box-shadow 0.2s ease; }
.act-card:hover { transform: translateY(-4px);
                  box-shadow: 0 12px 32px rgba(0,0,0,0.18) !important; }
</style>
""", unsafe_allow_html=True)

# ── Données ─────────────────────────────────────────────────────────────────────
df_p = load_participation_nationale()
t1   = df_p[df_p.tour == 1].sort_values("annee")
t2   = df_p[df_p.tour == 2].sort_values("annee")

try:
    df_scen  = load_scenarios_2027()
    pred_base = float(df_scen[df_scen.scenario == "baseline"]["abstention_nationale_pred (%)"].iloc[0])
    pred_max  = float(df_scen["abstention_nationale_pred (%)"].max())
except Exception:
    pred_base, pred_max = 29.3, 30.6

abs_2022 = float(t1[t1.annee == 2022]["taux_abstention"].iloc[0])
abs_1995 = float(t1[t1.annee == 1995]["taux_abstention"].iloc[0])
abs_2002 = float(t1[t1.annee == 2002]["taux_abstention"].iloc[0])
abs_2007 = float(t1[t1.annee == 2007]["taux_abstention"].iloc[0])
delta    = abs_2022 - abs_1995

# ── SVG sparkline (inline dans le hero) ─────────────────────────────────────────
# Données T1 : 1995 21.2 | 2002 28.4 | 2007 16.2 | 2012 20.5 | 2017 19.9 | 2022 26.3
# SVG 320×80, Y = 74 - ((val-14)/17)*66
def _y(v): return round(74 - ((v - 14) / 17) * 66, 1)
pts   = [(0,_y(21.2)),(64,_y(28.4)),(128,_y(16.2)),(192,_y(20.5)),(256,_y(19.9)),(320,_y(26.3))]
line  = " ".join(f"{x},{y}" for x,y in pts)
poly  = line + f" 320,80 0,80"
# 2027 prediction dot
x27, y27 = 370, _y(29.3)

# ── HERO ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #080f1c 0%, #0d1b35 55%, #112244 100%);
    border-radius: 16px;
    padding: 52px 48px 44px;
    margin-bottom: 4px;
    position: relative;
    overflow: hidden;
">
  <!-- Grain texture overlay -->
  <div style="position:absolute;inset:0;background:url('data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%224%22 height=%224%22><rect width=%224%22 height=%224%22 fill=%22%23ffffff08%22/><rect x=%220%22 y=%220%22 width=%221%22 height=%221%22 fill=%22%23ffffff06%22/></svg>');opacity:0.4;border-radius:16px;pointer-events:none;"></div>

  <div style="display:flex;align-items:flex-start;gap:32px;position:relative;">

    <!-- Texte gauche -->
    <div style="flex:1;min-width:0;">
      <p style="color:rgba(255,255,255,0.45);font-size:0.68rem;font-weight:700;
        letter-spacing:2.5px;text-transform:uppercase;margin:0 0 20px;">
        Analyse · France · 1995 – 2027
      </p>
      <h1 class="hero-num" style="
        color:#ffffff;font-size:clamp(2.2rem,4vw,3.2rem);font-weight:800;
        line-height:1.1;margin:0 0 6px;letter-spacing:-1px;border:none;">
        L'abstention&nbsp;—
      </h1>
      <h1 class="hero-num" style="
        color:#ffffff;font-size:clamp(2.2rem,4vw,3.2rem);font-weight:800;
        line-height:1.1;margin:0 0 24px;letter-spacing:-1px;border:none;
        animation-delay:0.1s;">
        trente ans de silence
      </h1>
      <p class="hero-sub" style="color:rgba(255,255,255,0.72);font-size:1rem;
        margin:0 0 32px;max-width:500px;line-height:1.65;animation-delay:0.2s;">
        En 1995, <strong style="color:#fff;">1 Français sur 5</strong> ne votait pas au premier tour.
        En 2022, c'est <strong style="color:#fff;">1 sur 4</strong>.
        Ce projet retrace trente ans de désengagement, cartographie ses causes,
        et projette ce que 2027 pourrait réserver.
      </p>

      <!-- Mini-stats dans le hero -->
      <div style="display:flex;gap:24px;flex-wrap:wrap;">
        <div style="background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.12);
          border-radius:8px;padding:12px 18px;">
          <p style="color:#7ab8f5;font-size:1.5rem;font-weight:700;margin:0;line-height:1;">{abs_2022:.1f}%</p>
          <p style="color:rgba(255,255,255,0.5);font-size:0.72rem;margin:2px 0 0;">abstention T1 2022</p>
        </div>
        <div style="background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.12);
          border-radius:8px;padding:12px 18px;">
          <p style="color:#fbbf24;font-size:1.5rem;font-weight:700;margin:0;line-height:1;">{abs_2002:.1f}%</p>
          <p style="color:rgba(255,255,255,0.5);font-size:0.72rem;margin:2px 0 0;">pic historique 2002</p>
        </div>
        <div style="background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.12);
          border-radius:8px;padding:12px 18px;">
          <p style="color:#34d399;font-size:1.5rem;font-weight:700;margin:0;line-height:1;">~{pred_base:.0f}%</p>
          <p style="color:rgba(255,255,255,0.5);font-size:0.72rem;margin:2px 0 0;">prédit 2027</p>
        </div>
      </div>
    </div>

    <!-- Sparkline SVG droite -->
    <div style="flex-shrink:0;display:flex;flex-direction:column;align-items:flex-end;gap:8px;">
      <p style="color:rgba(255,255,255,0.35);font-size:0.65rem;font-weight:600;
        letter-spacing:1px;text-transform:uppercase;margin:0;">Abstention T1 · 1995–2027</p>
      <svg viewBox="0 0 390 85" width="340" height="85" xmlns="http://www.w3.org/2000/svg">
        <!-- Fill area -->
        <defs>
          <linearGradient id="sparkFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.4"/>
            <stop offset="100%" stop-color="#3b82f6" stop-opacity="0.02"/>
          </linearGradient>
        </defs>
        <polygon points="{poly}" fill="url(#sparkFill)"/>
        <!-- Line -->
        <polyline points="{line}" fill="none" stroke="#60a5fa" stroke-width="2.5"
          stroke-linejoin="round" stroke-linecap="round"/>
        <!-- Points -->
        {''.join(f'<circle cx="{x}" cy="{y}" r="4" fill="#1d4ed8" stroke="#93c5fd" stroke-width="2"/>' for x,y in pts)}
        <!-- Labels années -->
        <text x="0" y="84" fill="rgba(255,255,255,0.35)" font-size="9" text-anchor="middle">1995</text>
        <text x="64" y="84" fill="rgba(255,255,255,0.35)" font-size="9" text-anchor="middle">2002</text>
        <text x="128" y="84" fill="rgba(255,255,255,0.35)" font-size="9" text-anchor="middle">2007</text>
        <text x="192" y="84" fill="rgba(255,255,255,0.35)" font-size="9" text-anchor="middle">2012</text>
        <text x="256" y="84" fill="rgba(255,255,255,0.35)" font-size="9" text-anchor="middle">2017</text>
        <text x="320" y="84" fill="rgba(255,255,255,0.35)" font-size="9" text-anchor="middle">2022</text>
        <!-- 2027 projection dashed -->
        <line x1="320" y1="{_y(26.3)}" x2="{x27}" y2="{y27}"
          stroke="#f59e0b" stroke-width="1.8" stroke-dasharray="4 3"/>
        <circle cx="{x27}" cy="{y27}" r="5" fill="#f59e0b" stroke="#fff" stroke-width="1.5"/>
        <text x="{x27}" y="{y27-9}" fill="#fbbf24" font-size="9" text-anchor="middle" font-weight="bold">2027</text>
      </svg>
    </div>

  </div>
</div>
""", unsafe_allow_html=True)

# ── 3 CHIFFRES CHOCS ────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1px;
  background:#e1e0d9;border-radius:12px;overflow:hidden;margin:8px 0 32px;">

  <div class="stat-card" style="background:#fff;padding:28px 28px 24px;">
    <p style="color:#898781;font-size:0.68rem;font-weight:700;letter-spacing:1.5px;
      text-transform:uppercase;margin:0 0 8px;">Tendance 1995 → 2022</p>
    <p style="color:#c0392b;font-size:3.2rem;font-weight:800;line-height:1;
      margin:0 0 4px;letter-spacing:-2px;">+{delta:.1f}<span style="font-size:1.6rem;">pp</span></p>
    <p style="color:#52514e;font-size:0.88rem;margin:0;line-height:1.5;">
      L'abstention a progressé de <strong>{abs_1995:.1f}%</strong> à <strong>{abs_2022:.1f}%</strong>
      en trente ans — une hausse structurelle, pas conjoncturelle.
    </p>
  </div>

  <div class="stat-card" style="background:#fff;padding:28px 28px 24px;">
    <p style="color:#898781;font-size:0.68rem;font-weight:700;letter-spacing:1.5px;
      text-transform:uppercase;margin:0 0 8px;">Ampleur du phénomène</p>
    <p style="color:#0d1b35;font-size:3.2rem;font-weight:800;line-height:1;
      margin:0 0 4px;letter-spacing:-2px;">1<span style="font-size:1.6rem;"> / </span>4</p>
    <p style="color:#52514e;font-size:0.88rem;margin:0;line-height:1.5;">
      Au premier tour 2022, <strong>1 Français sur 4 inscrit n'a pas voté</strong>.
      En 2002, le taux atteignait même <strong>{abs_2002:.1f}%</strong>.
    </p>
  </div>

  <div class="stat-card" style="background:#fff;padding:28px 28px 24px;">
    <p style="color:#898781;font-size:0.68rem;font-weight:700;letter-spacing:1.5px;
      text-transform:uppercase;margin:0 0 8px;">Projection T1 2027</p>
    <p style="color:#eda100;font-size:3.2rem;font-weight:800;line-height:1;
      margin:0 0 4px;letter-spacing:-2px;">{pred_base:.0f}<span style="font-size:1.6rem;">%</span></p>
    <p style="color:#52514e;font-size:0.88rem;margin:0;line-height:1.5;">
      Scénario de base du modèle Ridge — fourchette&nbsp;
      <strong>26 – {pred_max:.0f}%</strong> selon les scénarios,
      intégrant les législatives 2017 &amp; 2022.
    </p>
  </div>

</div>
""", unsafe_allow_html=True)

# ── GRAPHIQUE TENDANCE CENTRAL ──────────────────────────────────────────────────
annees = t1["annee"].values.astype(float)
vals   = t1["taux_abstention"].values
x_fit  = annees[annees >= 2007]
y_fit  = vals[annees >= 2007]
slope, intercept = np.polyfit(x_fit, y_fit, 1)
x_ext = np.linspace(2007, 2028, 150)

fig = go.Figure()

# Zone IC 80%
fig.add_trace(go.Scatter(
    x=[2027, 2027], y=[22.1, 34.2],
    mode="lines", line=dict(color="#eda100", width=16), opacity=0.15,
    showlegend=False, hoverinfo="skip",
))
# Droite tendance
fig.add_trace(go.Scatter(
    x=x_ext, y=intercept + slope * x_ext,
    mode="lines", name="Tendance (2007–2022)",
    line=dict(color="#2a78d6", width=1.5, dash="dash"),
    opacity=0.6, hoverinfo="skip",
))
# T2
fig.add_trace(go.Scatter(
    x=t2["annee"], y=t2["taux_abstention"],
    mode="lines+markers", name="Tour 2",
    line=dict(color="#c3c2b7", width=1.8, dash="dot"),
    marker=dict(size=7, color="#c3c2b7"),
    hovertemplate="<b>T2 %{x}</b> — %{y:.1f}%<extra></extra>",
))
# T1 — ligne + points
fig.add_trace(go.Scatter(
    x=t1["annee"], y=t1["taux_abstention"],
    mode="lines+markers", name="Tour 1",
    line=dict(color="#2a78d6", width=3),
    marker=dict(size=10, color="#2a78d6",
                line=dict(width=2.5, color="#ffffff")),
    hovertemplate="<b>T1 %{x}</b> — %{y:.1f}%<extra></extra>",
))
# Annotation 2002
fig.add_annotation(
    x=2002, y=abs_2002, text=f"Pic 2002 : {abs_2002:.1f}%",
    showarrow=True, arrowhead=2, arrowcolor="#52514e",
    ax=50, ay=-30, font=dict(color="#52514e", size=11, family="Inter"),
)
# Point 2027
fig.add_trace(go.Scatter(
    x=[2027], y=[pred_base],
    mode="markers", name=f"Préd. 2027 (~{pred_base:.0f}%)",
    marker=dict(size=16, color="#eda100", symbol="star",
                line=dict(width=2, color="#ffffff")),
    hovertemplate=f"<b>Projection 2027</b><br>Scénario de base : {pred_base:.1f}%<extra></extra>",
))
fig.add_vline(x=2022.5, line_dash="dot", line_color="#d0cfc8",
              line_width=1.2, annotation_text="→ Projection",
              annotation_position="top right",
              annotation_font=dict(color="#898781", size=10))

fig.update_layout(
    **PLOTLY_BASE,
    title=dict(
        text="<b>Taux d'abstention au 1er et 2e tour (1995–2022) + projection 2027</b>",
        font=dict(size=14, color="#0d0d0d"), x=0,
    ),
    yaxis=dict(**YAXIS_BASE, ticksuffix=" %", range=[10, 38],
               title="Taux d'abstention (%)"),
    xaxis=dict(**XAXIS_BASE, range=[1993, 2030], dtick=5),
    height=360,
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02,
        xanchor="left", x=0,
        font=dict(size=11, color="#52514e"),
        bgcolor="rgba(0,0,0,0)",
    ),
)
st.plotly_chart(fig, use_container_width=True)

# ── SÉPARATEUR ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:16px;margin:32px 0 28px;">
  <div style="flex:1;height:1px;background:#e1e0d9;"></div>
  <p style="color:#c3c2b7;font-size:0.7rem;font-weight:700;letter-spacing:2px;
    text-transform:uppercase;margin:0;white-space:nowrap;">L'analyse en trois actes</p>
  <div style="flex:1;height:1px;background:#e1e0d9;"></div>
</div>
""", unsafe_allow_html=True)

# ── 3 ACTES — cartes full-color ──────────────────────────────────────────────────
ACTES = [
    {
        "num": "01", "page": "pages/1_Desaffection.py",
        "bg": "linear-gradient(150deg,#0f2952 0%,#1c4a8a 100%)",
        "accent": "#7ab8f5",
        "emoji": "🗳️",
        "titre": "La désaffection",
        "hook": "Que s'est-il passé ?",
        "stat": f"+{delta:.0f} pp",
        "stat_label": "depuis 1995",
        "description": (
            "L'abstention au T1 a quasiment doublé en trente ans. "
            "La carte politique s'est simultanément recomposée : "
            "montée de l'extrême droite de 15% à 30%, émergence du Centre avec Macron."
        ),
    },
    {
        "num": "02", "page": "pages/2_Portrait.py",
        "bg": "linear-gradient(150deg,#0a3322 0%,#125c3c 100%)",
        "accent": "#6ee7b7",
        "emoji": "🗺️",
        "titre": "Le portrait",
        "hook": "Qui abstient, et où ?",
        "stat": "r = 0.41",
        "stat_label": "chômage × abstention",
        "description": (
            "4 profils de territoires identifiés par clustering. "
            "Le chômage est le prédicteur socio-économique le plus fort. "
            "Les \"territoires décrochés\" affichent 32% d'abstention moyenne."
        ),
    },
    {
        "num": "03", "page": "pages/3_2027.py",
        "bg": "linear-gradient(150deg,#5c3100 0%,#a05800 100%)",
        "accent": "#fcd34d",
        "emoji": "🔮",
        "titre": "Et 2027 ?",
        "hook": "Que peut-on projeter ?",
        "stat": f"~{pred_base:.0f}%",
        "stat_label": "scénario de base",
        "description": (
            "Deux méthodes complémentaires : tendance linéaire avec intervalles de confiance, "
            "et modèle Ridge par département. 4 scénarios dont « 2027 sans Macron ». "
            "Simulateur interactif en temps réel."
        ),
    },
]

c1, c2, c3 = st.columns(3, gap="large")
for col, acte in zip([c1, c2, c3], ACTES):
    with col:
        st.markdown(f"""
<div class="act-card" style="
    background: {acte['bg']};
    border-radius: 12px;
    padding: 30px 26px 26px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.12);
    height: 100%;
    position: relative;
    overflow: hidden;
">
  <!-- Numéro en watermark -->
  <p style="position:absolute;top:-10px;right:16px;font-size:6rem;font-weight:900;
    color:rgba(255,255,255,0.06);margin:0;line-height:1;user-select:none;">{acte['num']}</p>

  <p style="color:rgba(255,255,255,0.45);font-size:0.65rem;font-weight:700;
    letter-spacing:2px;text-transform:uppercase;margin:0 0 10px;">Acte {acte['num']}</p>
  <p style="font-size:1.8rem;margin:0 0 4px;">{acte['emoji']}</p>
  <h2 style="color:#ffffff;font-size:1.25rem;font-weight:700;margin:0 0 6px;
    border:none;padding:0;">{acte['titre']}</h2>
  <p style="color:{acte['accent']};font-size:0.82rem;font-style:italic;
    margin:0 0 16px;">{acte['hook']}</p>

  <!-- Stat centrale -->
  <div style="background:rgba(0,0,0,0.25);border-radius:8px;padding:14px 16px;margin-bottom:16px;">
    <p style="color:{acte['accent']};font-size:2rem;font-weight:800;margin:0;line-height:1;">
      {acte['stat']}</p>
    <p style="color:rgba(255,255,255,0.55);font-size:0.72rem;margin:2px 0 0;">
      {acte['stat_label']}</p>
  </div>

  <p style="color:rgba(255,255,255,0.75);font-size:0.83rem;line-height:1.6;margin:0 0 20px;">
    {acte['description']}</p>
</div>
""", unsafe_allow_html=True)
        st.page_link(acte["page"],
                     label=f"Ouvrir l'acte {acte['num']} →",
                     icon=acte["emoji"])

# ── FOOTER ───────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="border-top:1px solid #e1e0d9;padding-top:16px;
  display:flex;justify-content:space-between;align-items:flex-start;
  flex-wrap:wrap;gap:12px;">

  <div>
    <p style="color:#b0afa8;font-size:0.72rem;font-weight:700;letter-spacing:1px;
      text-transform:uppercase;margin:0 0 4px;">Sources</p>
    <p style="color:#c3c2b7;font-size:0.77rem;margin:0;line-height:1.55;">
      Ministère de l'Intérieur — résultats T1&T2, 1995–2022 (data.gouv.fr) ·
      INSEE — population par groupe d'âge (1975–2024) ·
      INSEE — chômage localisé 2022 · Filosofi — revenus 2021 ·
      Législatives 2017 &amp; 2022 (data.gouv.fr)
    </p>
  </div>

  <div style="text-align:right;">
    <p style="color:#b0afa8;font-size:0.72rem;font-weight:700;letter-spacing:1px;
      text-transform:uppercase;margin:0 0 4px;">Modèles</p>
    <p style="color:#c3c2b7;font-size:0.77rem;margin:0;line-height:1.55;">
      Ridge (sklearn) · LOYO CV · KMeans · Régression linéaire + IC (scipy)
    </p>
  </div>

</div>
""", unsafe_allow_html=True)
