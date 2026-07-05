"""
_style.py — palette, couleurs familles, layout Plotly partagés entre toutes les pages.
"""

import streamlit as st

# ── Couleurs familles politiques ────────────────────────────────────────────────
# Assignées dans l'ordre fixe de la palette de référence (slots 1-8) pour que
# l'identité d'une famille reste stable d'un graphique à l'autre.
COULEURS_FAMILLES = {
    "Droite":         "#2a78d6",  # slot 1 blue
    "Ecologie":       "#1baf7a",  # slot 2 aqua
    "Centre":         "#eda100",  # slot 3 yellow
    "Gauche":         "#e87ba4",  # slot 7 magenta
    "Souverainiste":  "#4a3aa7",  # slot 5 violet
    "Extrême gauche": "#e34948",  # slot 6 red
    "Extrême droite": "#898781",  # muted gray
    "Autre":          "#c3c2b7",  # light gray
}

# ── Config Plotly ───────────────────────────────────────────────────────────────
# Bases réutilisables pour les axes et la légende — à merger dans chaque chart
XAXIS_BASE  = dict(gridcolor="#e1e0d9", linecolor="#c3c2b7", tickfont=dict(color="#52514e"))
YAXIS_BASE  = dict(gridcolor="#e1e0d9", linecolor="#c3c2b7", tickfont=dict(color="#52514e"))
LEGEND_BASE = dict(
    orientation="h", yanchor="bottom", y=1.02,
    xanchor="left", x=0,
    font=dict(size=11, color="#52514e"),
    bgcolor="rgba(0,0,0,0)",
)

# Config Plotly commune (sans xaxis/yaxis/legend pour éviter les conflits de clés)
PLOTLY_BASE = dict(
    paper_bgcolor="#fcfcfb",
    plot_bgcolor="#fcfcfb",
    font=dict(
        family="system-ui, -apple-system, 'Segoe UI', sans-serif",
        color="#0b0b0b",
        size=12,
    ),
    margin=dict(l=8, r=8, t=48, b=8),
    hoverlabel=dict(bgcolor="white", bordercolor="#c3c2b7", font=dict(color="#0b0b0b")),
)


def inject_css():
    st.markdown("""
<style>
/* Fond général */
[data-testid="stAppViewContainer"] > .main { background-color: #f5f4f2; }
[data-testid="stHeader"]                   { background-color: #f5f4f2; }

/* Sidebar */
[data-testid="stSidebar"] { background-color: #eceae6; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    font-size: 0.85rem; color: #52514e;
}

/* Titres */
h1 { color: #0b0b0b; font-weight: 700; letter-spacing: -0.5px; }
h2 {
    color: #0b0b0b; font-weight: 600;
    border-left: 3px solid #2a78d6;
    padding-left: 10px; margin-top: 8px;
}
h3 { color: #52514e; font-weight: 500; }

/* Metric tiles */
[data-testid="stMetric"] {
    background: #fcfcfb;
    border: 1px solid #e1e0d9;
    border-radius: 8px;
    padding: 16px 20px;
}
[data-testid="stMetricValue"]  { color: #0b0b0b; }
[data-testid="stMetricDelta"]  { font-size: 0.8rem; }

/* Supprime le footer Streamlit */
footer { visibility: hidden; }
</style>""", unsafe_allow_html=True)


def carte_note(texte: str):
    """Bloc narratif encadré sous un graphique."""
    st.markdown(
        f'<div style="background:#fcfcfb;border:1px solid #e1e0d9;border-radius:8px;'
        f'padding:14px 18px;color:#52514e;font-size:0.9rem;line-height:1.6;">{texte}</div>',
        unsafe_allow_html=True,
    )
