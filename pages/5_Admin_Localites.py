import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.sql import text

st.set_page_config(page_title="Admin - Localités", layout="wide")
st.title("🔧 Page d'administration des localités")

db = st.secrets["database"]
engine = create_engine(f"postgresql://{db.user}:{db.password}@{db.host}:{db.port}/{db.dbname}")

# Lecture
df = pd.read_sql("SELECT * FROM zones_localites ORDER BY id", engine)
st.dataframe(df, use_container_width=True)

# Supprimer
id_to_delete = st.number_input("ID à supprimer :", min_value=1, step=1)
if st.button("🗑️ Supprimer la ligne"):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM zones_localites WHERE id = :id"), {"id": id_to_delete})
        st.success(f"Ligne {id_to_delete} supprimée.")
        st.rerun()
