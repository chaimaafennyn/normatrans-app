import streamlit as st
import pandas as pd
from database import get_engine

# === Authentification
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🚫 Accès non autorisé. Veuillez vous connecter depuis la page principale.")
    st.stop()

# === Vérification du rôle
if st.session_state.get("role") != "admin":
    st.error("🔒 Accès réservé à l'administrateur.")
    st.stop()

st.title("🕵️ Historique des actions")

engine = get_engine()
df_logs = pd.read_sql("SELECT * FROM logs ORDER BY timestamp DESC", engine)

st.dataframe(df_logs)
