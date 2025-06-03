import streamlit as st
import pandas as pd
import pandasql as psql

st.title("🤖 Assistant Données (mode simplifié)")

uploaded_file = st.file_uploader("📄 Uploader un fichier CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=";", encoding="latin1")
    st.dataframe(df.head())

    st.markdown("💬 Pose ta question (ex : `SELECT Zone, AVG(Distance_km) FROM df GROUP BY Zone`)")
    question = st.text_area("Votre requête SQL ici 👇")

    if st.button("🧠 Interroger les données"):
        try:
            result = psql.sqldf(question, locals())
            st.success("✅ Résultat obtenu :")
            st.dataframe(result)
        except Exception as e:
            st.error(f"❌ Erreur : {e}")
