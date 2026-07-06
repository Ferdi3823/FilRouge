"""
_style.py — palette, couleurs familles, layout Plotly et CSS global.
"""

import streamlit as st

# ── Couleurs familles politiques ────────────────────────────────────────────────
COULEURS_FAMILLES = {
    "Droite":         "#2a78d6",
    "Ecologie":       "#1baf7a",
    "Centre":         "#eda100",
    "Gauche":         "#e87ba4",
    "Souverainiste":  "#4a3aa7",
    "Extrême gauche": "#e34948",
    "Extrême droite": "#6b6b6b",
    "Autre":          "#c3c2b7",
}

# ── Config Plotly ───────────────────────────────────────────────────────────────
XAXIS_BASE = dict(
    gridcolor="#ebebea", linecolor="#d0cfc8",
    tickfont=dict(color="#6b6b6b", size=11),
    title_font=dict(color="#444", size=12),
    zeroline=False,
)
YAXIS_BASE = dict(
    gridcolor="#ebebea", linecolor="#d0cfc8",
    tickfont=dict(color="#6b6b6b", size=11),
    title_font=dict(color="#444", size=12),
    zeroline=False,
)
LEGEND_BASE = dict(
    orientation="h", yanchor="bottom", y=1.02,
    xanchor="left", x=0,
    font=dict(size=11, color="#52514e"),
    bgcolor="rgba(0,0,0,0)",
    borderwidth=0,
)
PLOTLY_BASE = dict(
    paper_bgcolor="#ffffff",
    plot_bgcolor="#fafaf9",
    font=dict(
        family="'Inter', 'Segoe UI', system-ui, sans-serif",
        color="#1a1a1a",
        size=12,
    ),
    margin=dict(l=12, r=12, t=52, b=12),
    hoverlabel=dict(
        bgcolor="white",
        bordercolor="#d0cfc8",
        font=dict(color="#1a1a1a", size=12),
    ),
    title_font=dict(size=14, color="#1a1a1a", family="'Inter', sans-serif"),
)


def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ── Fond & layout ─────────────────────────────────────────── */
[data-testid="stAppViewContainer"] > .main {
    background: #f4f3f0;
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}
[data-testid="stHeader"] {
    background: transparent;
    backdrop-filter: blur(8px);
}
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1200px;
}

/* ── Sidebar ───────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a2c50 0%, #1e3461 100%);
    border-right: none;
}
[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.88) !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    font-size: 0.82rem;
    color: rgba(255,255,255,0.60) !important;
    line-height: 1.5;
}
[data-testid="stSidebar"] a {
    color: #7ab8f5 !important;
    text-decoration: none;
}
[data-testid="stSidebarNav"] a {
    border-radius: 6px;
    padding: 6px 10px;
    transition: background 0.15s;
}
[data-testid="stSidebarNav"] a:hover,
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: rgba(255,255,255,0.12) !important;
}
[data-testid="stSidebarNav"] span {
    font-size: 0.88rem !important;
    font-weight: 500 !important;
}

/* ── Typographie ───────────────────────────────────────────── */
h1 {
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    color: #0d0d0d !important;
    letter-spacing: -0.6px;
    line-height: 1.2 !important;
    margin-bottom: 0.4rem !important;
}
h2 {
    font-size: 1.25rem !important;
    font-weight: 600 !important;
    color: #1a1a1a !important;
    border-left: 4px solid #2a78d6;
    padding-left: 12px;
    margin-top: 1.2rem !important;
    margin-bottom: 0.6rem !important;
}
h3 {
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: #2a2a2a !important;
    margin-top: 1rem !important;
    margin-bottom: 0.4rem !important;
}
p, li {
    font-size: 0.93rem;
    color: #3a3a3a;
    line-height: 1.65;
}

/* ── Metric tiles ──────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e5e4dd;
    border-radius: 10px;
    padding: 18px 20px 14px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    transition: box-shadow 0.2s;
}
[data-testid="stMetric"]:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.09);
}
[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
    color: #7a7975 !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    color: #0d0d0d !important;
    line-height: 1.1 !important;
}
[data-testid="stMetricDelta"] { font-size: 0.78rem !important; }

/* ── Charts / Plotly ───────────────────────────────────────── */
[data-testid="stPlotlyChart"] {
    background: #ffffff;
    border: 1px solid #e5e4dd;
    border-radius: 10px;
    padding: 8px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

/* ── Sliders ───────────────────────────────────────────────── */
[data-testid="stSlider"] > div > div > div {
    background: #2a78d6 !important;
}
[data-testid="stSlider"] [data-testid="stTickBar"] {
    color: #7a7975 !important;
    font-size: 0.75rem !important;
}

/* ── Radio buttons ─────────────────────────────────────────── */
[data-testid="stRadio"] label {
    background: #ffffff;
    border: 1px solid #e5e4dd;
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 0.85rem !important;
    transition: all 0.15s;
    cursor: pointer;
}
[data-testid="stRadio"] label:hover {
    border-color: #2a78d6;
    color: #2a78d6;
}

/* ── Tabs ──────────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tab"] {
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: #6b6b6b !important;
    border-bottom: 2px solid transparent;
    padding: 8px 18px !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #2a78d6 !important;
    border-bottom: 2px solid #2a78d6 !important;
    font-weight: 600 !important;
}

/* ── Select / Expander ─────────────────────────────────────── */
[data-testid="stExpander"] {
    background: #ffffff;
    border: 1px solid #e5e4dd !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary {
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: #3a3a3a !important;
}

/* ── Page links ────────────────────────────────────────────── */
[data-testid="stPageLink"] a {
    display: inline-block;
    margin-top: 10px;
    padding: 7px 16px;
    background: #2a78d6;
    color: white !important;
    border-radius: 6px;
    font-size: 0.83rem !important;
    font-weight: 600 !important;
    text-decoration: none;
    transition: background 0.15s;
}
[data-testid="stPageLink"] a:hover { background: #1c5cab; }

/* ── Divider ───────────────────────────────────────────────── */
hr { border-color: #e5e4dd !important; margin: 1.5rem 0 !important; }

/* ── Caption ───────────────────────────────────────────────── */
[data-testid="stCaptionContainer"] {
    color: #8a8880 !important;
    font-size: 0.78rem !important;
}

/* ── Masque footer Streamlit ───────────────────────────────── */
footer, #MainMenu, [data-testid="stToolbar"] { visibility: hidden; }
</style>""", unsafe_allow_html=True)

    # Injection sidebar logo + meta
    st.sidebar.markdown("""
<div style="padding: 16px 8px 20px; border-bottom: 1px solid rgba(255,255,255,0.12); margin-bottom: 16px;">
  <p style="font-size:0.65rem; font-weight:700; letter-spacing:1.8px; text-transform:uppercase;
            color:rgba(255,255,255,0.45); margin:0 0 4px;">Analyse · France</p>
  <p style="font-size:1rem; font-weight:700; color:#ffffff; margin:0; line-height:1.3;">
    Présidentielles<br>1995 – 2027
  </p>
</div>
<div style="padding: 0 8px;">
  <p style="font-size:0.70rem; font-weight:600; letter-spacing:1.2px; text-transform:uppercase;
            color:rgba(255,255,255,0.35); margin:0 0 8px;">Navigation</p>
</div>
""", unsafe_allow_html=True)


def carte_note(texte: str):
    """Bloc narratif encadré sous un graphique."""
    st.markdown(
        f'<div style="background:#f8f8f6;border-left:3px solid #d0cfc8;border-radius:0 6px 6px 0;'
        f'padding:12px 16px;color:#5a5955;font-size:0.83rem;line-height:1.65;'
        f'margin-top:8px;">'
        f'<span style="color:#2a78d6;font-weight:600;">Note — </span>{texte}</div>',
        unsafe_allow_html=True,
    )


def section_title(titre: str, subtitle: str = ""):
    """Titre de section avec sous-titre optionnel."""
    html = f'<div style="margin: 1.5rem 0 0.8rem;">'
    html += f'<h3 style="margin:0 0 4px;font-size:1.05rem;font-weight:700;color:#1a1a1a;">{titre}</h3>'
    if subtitle:
        html += f'<p style="margin:0;font-size:0.83rem;color:#7a7975;">{subtitle}</p>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def stat_badge(label: str, value: str, color: str = "#2a78d6"):
    """Badge inline pour mettre en valeur une stat."""
    return (
        f'<span style="display:inline-block;background:{color}18;color:{color};'
        f'border:1px solid {color}44;border-radius:4px;padding:2px 8px;'
        f'font-size:0.8rem;font-weight:600;">{label}: {value}</span>'
    )
