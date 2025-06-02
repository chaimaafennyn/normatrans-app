import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import get_engine

st.set_page_config(page_title="🛠️ Gestion des Localités", layout="wide")

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🚫 Accès non autorisé. Veuillez vous connecter depuis la page principale.")
    st.stop()
