import streamlit as st
import pandas as pd

st.header("📦 Analyse des Expéditions")

default_global_file = "repartition_par_zone.csv"
default_agence_file = "repartition_par_agence_et_zone.csv"

uploaded_global = st.file_uploader("📁 Uploader le fichier global (optionnel)", type=["csv"])
uploaded_agence = st.file_uploader("📁 Uploader le fichier par agence (optionnel)", type=["csv"])

try:
    df_global = pd.read_csv(uploaded_global if uploaded_global else default_global_file, sep=";", encoding="utf-8")
    df_agence = pd.read_csv(uploaded_agence if uploaded_agence else default_agence_file, sep=";", encoding="utf-8")
    st.success("✅ Fichiers chargés avec succès")
except Exception as e:
    st.error(f"Erreur de chargement des fichiers : {e}")
    st.stop()

df_global = df_global.rename(columns={"% d'expéditions": "Pourcentage"})
df_agence = df_agence.rename(columns={"% d'expéditions": "Pourcentage"})

for df in [df_global, df_agence]:
    df["Pourcentage"] = df["Pourcentage"].astype(str).str.replace(",", ".").astype(float)

st.subheader("🌍 Répartition globale par zone")
st.dataframe(df_global)
st.bar_chart(df_global.set_index("Zone")["Pourcentage"])

st.subheader("🏢 Répartition par agence")
agence_choisie = st.selectbox("Sélectionnez une agence :", df_agence["Code agence"].unique())
df_agence_filtre = df_agence[df_agence["Code agence"] == agence_choisie]
st.dataframe(df_agence_filtre)
st.bar_chart(df_agence_filtre.set_index("Zone")["Pourcentage"])

st.download_button(
    label="📥 Télécharger la répartition globale",
    data=df_global.to_csv(index=False).encode("utf-8"),
    file_name="repartition_globale_par_zone.csv",
    mime="text/csv"
)

st.download_button(
    label=f"📥 Télécharger les données de l'agence {agence_choisie}",
    data=df_agence_filtre.to_csv(index=False).encode("utf-8"),
    file_name=f"repartition_{agence_choisie}.csv",
    mime="text/csv"
)
