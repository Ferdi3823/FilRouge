"""
Baromètre 2027 — Sondages d'intention d'abstention
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from data_loader import load_sondages_2027, load_linear_prediction, load_participation_nationale
from _style import (inject_css, PLOTLY_BASE, XAXIS_BASE, YAXIS_BASE,
                    LEGEND_BASE, carte_note, section_title)

st.set_page_config(
    page_title="Baromètre 2027 — Sondages",
    page_icon="📊",
    layout="wide",
)
inject_css()

# ── En-tête ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#4a3aa7 0%,#6c4fc4 100%);
border-radius:10px;padding:28px 32px 22px;margin-bottom:24px;">
  <p style="color:rgba(255,255,255,0.6);font-size:0.72rem;font-weight:700;
  letter-spacing:1.5px;text-transform:uppercase;margin:0 0 6px;">Données complémentaires</p>
  <h1 style="color:#fff;font-size:1.7rem;margin:0 0 10px;border:none;">📊 Baromètre 2027</h1>
  <p style="color:rgba(255,255,255,0.88);font-size:0.95rem;margin:0;max-width:640px;">
    Les sondages d'intention d'abstention publiés avant l'élection — une source externe
    à confronter avec nos modèles statistiques.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Données ─────────────────────────────────────────────────────────────────────
try:
    df_s = load_sondages_2027()
except Exception:
    df_s = None

try:
    df_lin = load_linear_prediction()
    t1_lin = df_lin[df_lin["tour"] == 1].iloc[0]
    model_pred = float(t1_lin["pred"])
    model_ci80_low  = float(t1_lin["ci80_low"])
    model_ci80_high = float(t1_lin["ci80_high"])
except Exception:
    model_pred = None

try:
    df_partic = load_participation_nationale()
except Exception:
    df_partic = None

if df_s is None or df_s.empty:
    st.warning("Fichier sondages_2027.csv introuvable.")
    st.stop()

s_t1 = df_s[df_s["tour"] == 1].reset_index(drop=True)

# ── Section 1 : Cartes sondages ──────────────────────────────────────────────
section_title("Les sondages disponibles",
              "Intention d'abstention au 1er tour — données illustratives à titre académique")

POLL_COLORS = ["#9b59b6", "#e34948", "#2a78d6", "#1baf7a"]

cols = st.columns(len(s_t1))
for col, (_, row), pc in zip(cols, s_t1.iterrows(), POLL_COLORS):
    col.markdown(f"""
<div style="background:#fcfcfb;border:1px solid #e1e0d9;border-top:4px solid {pc};
border-radius:10px;padding:24px;text-align:center;height:100%;">
  <p style="color:#898781;font-size:0.68rem;font-weight:700;letter-spacing:1.2px;
  text-transform:uppercase;margin:0 0 2px;">Sondage</p>
  <p style="color:#0b0b0b;font-size:0.9rem;font-weight:600;margin:0 0 6px;
  line-height:1.3;">{row['source']}</p>
  <p style="color:{pc};font-size:0.82rem;font-weight:600;margin:0 0 14px;">
    {row['date_label']}</p>
  <p style="color:#0b0b0b;font-size:2.6rem;font-weight:700;margin:0 0 2px;line-height:1;">
    {row['intention_abstention']:.1f} %</p>
  <p style="color:#52514e;font-size:0.85rem;font-weight:500;margin:0 0 10px;">
    intention d'abstention T1</p>
  <div style="background:{pc}18;border:1px solid {pc}44;border-radius:6px;
  padding:8px 12px;font-size:0.8rem;color:{pc};font-weight:600;">
    Marge : ± {row['marge']:.1f} pp
    &nbsp;·&nbsp;
    {row['intention_abstention']-row['marge']:.1f} – {row['intention_abstention']+row['marge']:.1f} %
  </div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Section 2 : Graphique comparatif sondages vs modèle ─────────────────────
section_title("Comparaison : sondages vs modèle",
              "Toutes les estimations pour 2027 sur une même échelle")

if model_pred is not None:
    fig_comp = go.Figure()

    # Bande IC modèle
    fig_comp.add_shape(
        type="rect",
        x0=-0.5, x1=len(s_t1) + 0.5,
        y0=model_ci80_low, y1=model_ci80_high,
        fillcolor="#2a78d6", opacity=0.07,
        line=dict(width=0),
        layer="below",
    )
    fig_comp.add_hline(
        y=model_pred,
        line=dict(color="#2a78d6", width=2, dash="dash"),
        annotation_text=f"Modèle tendance : {model_pred:.1f}%",
        annotation_position="top left",
        annotation_font=dict(color="#2a78d6", size=11),
    )

    # Points sondages
    for i, (_, row) in enumerate(s_t1.iterrows()):
        pc = POLL_COLORS[i % len(POLL_COLORS)]
        sym = ["diamond", "triangle-up", "circle", "square"][i % 4]
        fig_comp.add_trace(go.Scatter(
            x=[row["source"]],
            y=[row["intention_abstention"]],
            mode="markers",
            name=f"{row['source']} ({row['date_label']})",
            marker=dict(size=16, color=pc, symbol=sym,
                        line=dict(width=2, color="#ffffff")),
            error_y=dict(type="constant", value=row["marge"],
                         color=pc, thickness=2.5, width=8),
            hovertemplate=(
                f"<b>{row['source']}</b><br>"
                f"{row['date_label']}<br>"
                f"Intention abstention T1 : <b>{row['intention_abstention']:.1f} %</b><br>"
                f"Marge : ± {row['marge']:.1f} pp<extra></extra>"
            ),
        ))

    # Consensus pondéré
    weights = 1.0 / (s_t1["marge"] ** 2)
    poll_consensus = float((s_t1["intention_abstention"] * weights).sum() / weights.sum())
    consensus = 0.5 * model_pred + 0.5 * poll_consensus

    fig_comp.add_hline(
        y=consensus,
        line=dict(color="#c0392b", width=2.5),
        annotation_text=f"Consensus : {consensus:.1f}%",
        annotation_position="bottom right",
        annotation_font=dict(color="#c0392b", size=12, family="Inter"),
    )

    fig_comp.update_layout(
        **PLOTLY_BASE,
        yaxis=dict(**YAXIS_BASE, ticksuffix=" %", range=[22, 40],
                   title="Intention d'abstention T1 (%)"),
        xaxis=dict(**XAXIS_BASE, title="Source"),
        height=380,
        showlegend=False,
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    carte_note(
        f"Ligne pointillée bleue : tendance linéaire du modèle ({model_pred:.1f}%). "
        f"Ligne rouge pleine : consensus pondéré (50% modèle + 50% sondages) = {consensus:.1f}%. "
        "Les barres d'erreur représentent la marge déclarée par chaque institut."
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Section 3 : Timeline des sondages ────────────────────────────────────────
section_title("Timeline des sondages",
              "Évolution des estimations dans le temps avant l'élection")

if model_pred is not None and df_partic is not None:
    fig_tl = go.Figure()

    # Historique présidentielles
    partic_t1 = df_partic[df_partic["tour"] == 1].sort_values("annee")
    fig_tl.add_trace(go.Scatter(
        x=partic_t1["annee"],
        y=partic_t1["taux_abstention"],
        mode="lines+markers",
        name="Résultat officiel T1",
        line=dict(color="#2a78d6", width=2.5),
        marker=dict(size=7, color="#2a78d6"),
        hovertemplate="<b>%{x}</b> — Résultat : %{y:.1f}%<extra></extra>",
    ))

    # Droite de tendance projetée jusqu'en 2027
    x_h = partic_t1[partic_t1["annee"] >= 2007]["annee"].values.astype(float)
    y_h = partic_t1[partic_t1["annee"] >= 2007]["taux_abstention"].values
    slope, intercept = np.polyfit(x_h, y_h, 1)
    x_ext = np.linspace(2007, 2027.5, 100)
    fig_tl.add_trace(go.Scatter(
        x=x_ext, y=intercept + slope * x_ext,
        mode="lines", name="Tendance linéaire",
        line=dict(color="#2a78d6", width=1.2, dash="dash"),
        showlegend=True, hoverinfo="skip",
    ))

    # Prédiction modèle 2027
    fig_tl.add_trace(go.Scatter(
        x=[2027], y=[model_pred],
        mode="markers", name=f"Modèle ({model_pred:.1f}%)",
        marker=dict(size=14, color="#2a78d6", symbol="star"),
        hovertemplate=f"<b>Modèle 2027</b><br>Prédiction : {model_pred:.1f}%<extra></extra>",
    ))

    # Sondages — positionnés sur l'axe temporel par mois_num
    for i, (_, row) in enumerate(s_t1.iterrows()):
        pc = POLL_COLORS[i % len(POLL_COLORS)]
        sym = ["diamond", "triangle-up"][i % 2]
        x_poll = 2027 + row["mois_num"] / 12
        fig_tl.add_trace(go.Scatter(
            x=[x_poll], y=[row["intention_abstention"]],
            mode="markers",
            name=f"{row['source']} ({row['date_label']})",
            marker=dict(size=13, color=pc, symbol=sym,
                        line=dict(width=1.5, color="#ffffff")),
            error_y=dict(type="constant", value=row["marge"],
                         color=pc, thickness=2, width=6),
            hovertemplate=(
                f"<b>{row['source']}</b><br>{row['date_label']}<br>"
                f"Intention : {row['intention_abstention']:.1f}% ± {row['marge']:.1f}pp<extra></extra>"
            ),
        ))

    fig_tl.add_vline(x=2022.5, line_dash="dot", line_color="#898781", line_width=1,
                     annotation_text="→ 2027", annotation_position="top right")

    fig_tl.update_layout(
        **PLOTLY_BASE,
        yaxis=dict(**YAXIS_BASE, ticksuffix=" %", range=[15, 42],
                   title="Taux d'abstention (%)"),
        xaxis=dict(**XAXIS_BASE, range=[1993, 2028], dtick=5,
                   title="Année"),
        height=400,
        legend=LEGEND_BASE,
    )
    st.plotly_chart(fig_tl, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Section 4 : Méthodologie ─────────────────────────────────────────────────
section_title("Note méthodologique",
              "Limites et précautions d'interprétation")

st.markdown("""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:8px;">

<div style="background:#fff8e1;border:1px solid #f0d080;border-radius:8px;padding:16px;">
  <p style="font-weight:600;color:#8a6000;font-size:0.9rem;margin:0 0 8px;">
    ⚠️ Biais déclaratif
  </p>
  <p style="color:#5a4800;font-size:0.83rem;margin:0;line-height:1.6;">
    Les sondages d'intention surestiment systématiquement l'abstention déclarée :
    il est socialement plus acceptable de dire "je ne sais pas si je voterai" que
    de confirmer un vote. L'écart moyen constaté en France : <strong>+3 à 5 points</strong>
    d'intention vs résultat réel.
  </p>
</div>

<div style="background:#e8f4fd;border:1px solid #aad4f5;border-radius:8px;padding:16px;">
  <p style="font-weight:600;color:#0c5a8a;font-size:0.9rem;margin:0 0 8px;">
    📅 Horizon temporel
  </p>
  <p style="color:#0a3d5e;font-size:0.83rem;margin:0;line-height:1.6;">
    Les sondages à 1–4 mois de l'élection sont moins fiables qu'à J−2 semaines.
    L'intention d'abstention fluctue selon l'actualité politique (candidats,
    débats, crises). Ces données sont indicatives de la <strong>tendance perçue</strong>,
    non d'un résultat arrêté.
  </p>
</div>

<div style="background:#f0fff4;border:1px solid #a8ddb5;border-radius:8px;padding:16px;">
  <p style="font-weight:600;color:#1a6b37;font-size:0.9rem;margin:0 0 8px;">
    🔬 Représentativité
  </p>
  <p style="color:#124d28;font-size:0.83rem;margin:0;line-height:1.6;">
    La marge d'erreur déclarée (±2–2,5 pp) correspond à un intervalle de confiance
    à 95% sur un échantillon de ~1000 personnes. Elle ne tient pas compte des
    biais de recrutement (panel en ligne) ni du <em>late-deciding effect</em>.
  </p>
</div>

<div style="background:#fdf0ff;border:1px solid #d9a8e8;border-radius:8px;padding:16px;">
  <p style="font-weight:600;color:#6a0080;font-size:0.9rem;margin:0 0 8px;">
    🤖 Consensus modèle + sondages
  </p>
  <p style="color:#4a005a;font-size:0.83rem;margin:0;line-height:1.6;">
    Notre estimation consensus (50% modèle / 50% sondages pondérés) n'est pas
    une méthode académique établie — c'est une illustration du principe d'ensemble.
    En pratique, des pondérations variables selon la qualité des sources et
    l'horizon temporel seraient nécessaires.
  </p>
</div>

</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
carte_note(
    "Sources illustratives utilisées dans ce projet : Harris Interactive / Toluna (janv. 2027), "
    "Ifop / Paris Match (mars 2027). Ces données sont simulées à des fins académiques "
    "et ne reflètent pas des sondages réellement publiés."
)
