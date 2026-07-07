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
    gridcolor="#eae9e4", linecolor="#d4d3cc",
    tickfont=dict(color="#4a4a48", size=12),
    title_font=dict(color="#1a1a1a", size=13, family="'Inter', sans-serif"),
    zeroline=False,
)
YAXIS_BASE = dict(
    gridcolor="#eae9e4", linecolor="#d4d3cc",
    tickfont=dict(color="#4a4a48", size=12),
    title_font=dict(color="#1a1a1a", size=13, family="'Inter', sans-serif"),
    zeroline=False,
)
LEGEND_BASE = dict(
    orientation="h", yanchor="bottom", y=1.02,
    xanchor="left", x=0,
    font=dict(size=12, color="#2a2a2a", family="'Inter', sans-serif"),
    bgcolor="rgba(255,255,255,0.9)",
    borderwidth=0,
)
PLOTLY_BASE = dict(
    paper_bgcolor="#ffffff",
    plot_bgcolor="#fafaf8",
    font=dict(
        family="'Inter', 'Segoe UI', system-ui, sans-serif",
        color="#1a1a1a",
        size=13,
    ),
    margin=dict(l=16, r=16, t=56, b=16),
    hoverlabel=dict(
        bgcolor="white",
        bordercolor="#c8c7c0",
        font=dict(color="#0a0a0a", size=13, family="'Inter', sans-serif"),
    ),
    title_font=dict(size=15, color="#0a0a0a", family="'Inter', sans-serif"),
)


def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

/* ── Reset & variables ──────────────────────────────────────── */
:root {
    --clr-bg:      #f2f1ee;
    --clr-surface: #ffffff;
    --clr-border:  #e0dfd8;
    --clr-text:    #1a1a1a;
    --clr-text-2:  #4a4a48;
    --clr-text-3:  #7a7975;
    --clr-blue:    #2563eb;
    --clr-blue-dk: #1a4fc4;
    --font:        'Inter', 'Segoe UI', system-ui, sans-serif;
}

/* ── Fond & layout ──────────────────────────────────────────── */
[data-testid="stAppViewContainer"] > .main {
    background: var(--clr-bg);
    font-family: var(--font);
}
[data-testid="stHeader"] { background: transparent; }
.block-container {
    padding-top: 1.4rem !important;
    padding-bottom: 3rem !important;
    max-width: 1200px;
}

/* ── Sidebar ────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1f3d 0%, #162847 100%);
    border-right: none;
}
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.88) !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    font-size: 0.83rem;
    color: rgba(255,255,255,0.55) !important;
    line-height: 1.55;
}
[data-testid="stSidebar"] a { color: #93c5fd !important; text-decoration: none; }
[data-testid="stSidebarNav"] a {
    border-radius: 7px; padding: 7px 12px; transition: background 0.15s;
}
[data-testid="stSidebarNav"] a:hover,
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: rgba(255,255,255,0.13) !important;
}
[data-testid="stSidebarNav"] span {
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.1px;
}

/* ── Typographie corps ──────────────────────────────────────── */
h1 {
    font-size: 1.85rem !important;
    font-weight: 800 !important;
    color: #0d0d0d !important;
    letter-spacing: -0.8px !important;
    line-height: 1.15 !important;
    margin-bottom: 0.35rem !important;
    border: none !important;
}
h2 {
    font-size: 1.2rem !important;
    font-weight: 700 !important;
    color: #111 !important;
    border-left: 4px solid var(--clr-blue);
    padding-left: 13px;
    margin-top: 1.4rem !important;
    margin-bottom: 0.5rem !important;
    letter-spacing: -0.2px;
}
h3 {
    font-size: 1.0rem !important;
    font-weight: 700 !important;
    color: #1a1a1a !important;
    margin-top: 0.9rem !important;
    margin-bottom: 0.35rem !important;
}
p { font-size: 0.95rem; color: var(--clr-text-2); line-height: 1.7; }
li { font-size: 0.93rem; color: var(--clr-text-2); line-height: 1.65; }
strong { color: var(--clr-text) !important; font-weight: 600; }

/* ── Metric tiles ───────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--clr-surface);
    border: 1px solid var(--clr-border);
    border-radius: 10px;
    padding: 18px 20px 14px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s;
}
[data-testid="stMetric"]:hover { box-shadow: 0 4px 14px rgba(0,0,0,0.08); }
[data-testid="stMetricLabel"] {
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    color: var(--clr-text-3) !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.85rem !important;
    font-weight: 800 !important;
    color: #0a0a0a !important;
    line-height: 1.1 !important;
    letter-spacing: -1px;
}
[data-testid="stMetricDelta"] { font-size: 0.8rem !important; font-weight: 500 !important; }

/* ── Charts / Plotly ────────────────────────────────────────── */
[data-testid="stPlotlyChart"] {
    background: var(--clr-surface);
    border: 1px solid var(--clr-border);
    border-radius: 10px;
    padding: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* ── Sliders ────────────────────────────────────────────────── */
[data-testid="stSlider"] > div > div > div { background: var(--clr-blue) !important; }
[data-testid="stSlider"] [data-testid="stTickBar"] {
    color: var(--clr-text-3) !important; font-size: 0.75rem !important;
}
[data-testid="stSlider"] label {
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    color: var(--clr-text) !important;
}

/* ── Radio buttons ──────────────────────────────────────────── */
[data-testid="stRadio"] label {
    background: var(--clr-surface);
    border: 1.5px solid var(--clr-border);
    border-radius: 6px;
    padding: 7px 15px;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: var(--clr-text-2) !important;
    transition: all 0.15s;
    cursor: pointer;
}
[data-testid="stRadio"] label:hover { border-color: var(--clr-blue); color: var(--clr-blue) !important; }

/* ── Tabs ───────────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tab"] {
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    color: var(--clr-text-3) !important;
    padding: 9px 20px !important;
    border-bottom: 2px solid transparent;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--clr-blue) !important;
    border-bottom: 2.5px solid var(--clr-blue) !important;
    font-weight: 700 !important;
}

/* ── Expander ───────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: var(--clr-surface);
    border: 1px solid var(--clr-border) !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary {
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    color: var(--clr-text) !important;
}

/* ── Page links (boutons CTA) ───────────────────────────────── */
[data-testid="stPageLink"] a {
    display: inline-block;
    margin-top: 10px;
    padding: 8px 18px;
    background: var(--clr-blue);
    color: #ffffff !important;
    border-radius: 7px;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    text-decoration: none;
    letter-spacing: 0.1px;
    transition: background 0.15s, transform 0.1s;
}
[data-testid="stPageLink"] a:hover {
    background: var(--clr-blue-dk);
    transform: translateY(-1px);
}

/* ── Caption ────────────────────────────────────────────────── */
[data-testid="stCaptionContainer"] {
    color: var(--clr-text-3) !important;
    font-size: 0.8rem !important;
    line-height: 1.55 !important;
}

/* ── Divider ────────────────────────────────────────────────── */
hr { border-color: var(--clr-border) !important; margin: 1.6rem 0 !important; }

/* ── Selectbox / Input ──────────────────────────────────────── */
[data-testid="stSelectbox"] label,
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label {
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    color: var(--clr-text) !important;
}

/* ── Masque footer Streamlit ────────────────────────────────── */
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
        f'<div style="background:#f0efeb;border-left:3px solid #b0afa8;border-radius:0 7px 7px 0;'
        f'padding:13px 17px;color:#3a3a38;font-size:0.86rem;line-height:1.68;'
        f'margin-top:10px;">'
        f'<span style="color:#2563eb;font-weight:700;">Note — </span>{texte}</div>',
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
