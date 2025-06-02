import streamlit as st
from database import get_engine
import pandas as pd

# === Authentification
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🚫 Accès non autorisé. Veuillez vous connecter depuis la page principale.")
    st.stop()

st.title("🕵️ Historique des actions")

engine = get_engine()
df_logs = pd.read_sql("SELECT * FROM logs ORDER BY timestamp DESC", engine)
st.dataframe(df_logs)
