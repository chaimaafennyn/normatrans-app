import streamlit as st
import pandas as pd
import plotly.express as px

st.header("⚖️ Analyse des Poids")

default_file = "analyse_poids_par_agence_et_zones.csv"
uploaded_poids = st.file_uploader("Uploader un autre fichier des poids (optionnel)", type=["csv"])

if uploaded_poids is not None:
    df_poids = pd.read_csv(uploaded_poids, sep=";", encoding="latin-1")
    st.success("✅ Fichier poids chargé avec succès !")
else:
    df_poids = pd.read_csv(default_file, sep=";", encoding="latin-1")
    st.info(f"📂 Fichier par défaut utilisé : {default_file}")

df_poids.columns = df_poids.columns.str.strip()

try:
    df_poids["Poids_total"] = df_poids["Poids_total"].astype(str).str.replace(",", ".").astype(float)
    df_poids["% Poids"] = df_poids["% Poids"].astype(str).str.replace(",", ".").astype(float)

    st.subheader("📋 Détail par agence et par zone")
    st.dataframe(df_poids)

    st.subheader("📊 Répartition globale des poids par zone")
    poids_global = df_poids.groupby("Zone")["Poids_total"].sum().reset_index()
    poids_global["% Poids"] = 100 * poids_global["Poids_total"] / poids_global["Poids_total"].sum()
    st.dataframe(poids_global.round(2))

    fig = px.pie(poids_global, values="Poids_total", names="Zone", title="")
    st.plotly_chart(fig)

    st.download_button(
        label="📥 Télécharger les poids globaux",
        data=poids_global.to_csv(index=False).encode("utf-8"),
        file_name="repartition_poids_globale.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"❌ Erreur dans l’analyse des poids : {e}")
