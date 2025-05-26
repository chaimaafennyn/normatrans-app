import streamlit as st
from database import get_engine
import pandas as pd

st.title("🕵️ Historique des actions")

engine = get_engine()
df_logs = pd.read_sql("SELECT * FROM logs ORDER BY timestamp DESC", engine)
st.dataframe(df_logs)
