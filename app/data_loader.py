"""
data_loader.py
==============
Chargement centralisé des fichiers CSV produits par le pipeline.
Toutes les pages Streamlit importent depuis ce module.
"""

from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR  = BASE_DIR / "outputs"
TBL_DIR  = OUT_DIR  / "tables"


@st.cache_data
def load_elections_dept() -> pd.DataFrame:
    return pd.read_csv(OUT_DIR / "elections_dept.csv")


@st.cache_data
def load_elections_candidats() -> pd.DataFrame:
    return pd.read_csv(OUT_DIR / "elections_candidats.csv")


@st.cache_data
def load_demography() -> pd.DataFrame:
    return pd.read_csv(OUT_DIR / "elections_with_demography.csv")


@st.cache_data
def load_scores_familles() -> pd.DataFrame:
    return pd.read_csv(TBL_DIR / "scores_familles_t1.csv")


@st.cache_data
def load_participation_nationale() -> pd.DataFrame:
    return pd.read_csv(TBL_DIR / "participation_nationale.csv")


@st.cache_data
def load_scenarios_2027() -> pd.DataFrame:
    return pd.read_csv(TBL_DIR / "scenarios_2027.csv")


@st.cache_data
def load_predictions_2027() -> pd.DataFrame:
    return pd.read_csv(TBL_DIR / "predictions_2027_dept.csv")


@st.cache_data
def load_dept_clusters() -> pd.DataFrame:
    return pd.read_csv(TBL_DIR / "dept_clusters.csv")


@st.cache_data
def load_abstention_dept() -> pd.DataFrame:
    return pd.read_csv(TBL_DIR / "abstention_par_dept_annee.csv")


@st.cache_data
def load_linear_prediction() -> pd.DataFrame:
    return pd.read_csv(TBL_DIR / "linear_trend_prediction.csv")


@st.cache_data
def load_sondages_2027() -> pd.DataFrame:
    return pd.read_csv(BASE_DIR / "data" / "sondages_2027.csv")
