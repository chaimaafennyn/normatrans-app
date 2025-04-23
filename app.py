import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("Normatrans - Analyse des zones de livraison")

# Chargement des données
try:
    df = pd.read_csv("zones_final_localites.csv", sep=";", encoding="utf-8")
    df.columns = df.columns.str.strip()
    st.success("Données chargées avec succès")
except Exception as e:
    st.error(f"Erreur de chargement : {e}")
    st.stop()

# Vérification colonnes nécessaires
required_cols = ["Commune", "Code agence", "Latitude", "Longitude", "Zone", "Distance (km)", "Latitude_agence", "Longitude_agence"]
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    st.error(f"Colonnes manquantes : {missing_cols}")
    st.stop()

# Nettoyage
df = df.dropna(subset=["Latitude", "Longitude"])

# Interface de sélection
agences = df["Code agence"].dropna().unique()
agence_selectionnee = st.selectbox("Choisissez une agence :", agences)

# Filtrer les données selon l'agence choisie
df_agence = df[df["Code agence"] == agence_selectionnee]
coord_agence = df_agence[["Latitude_agence", "Longitude_agence"]].iloc[0]

# Statistiques
st.subheader("Statistiques générales")
col1, col2, col3 = st.columns(3)
col1.metric("Nombre de localités", len(df_agence))
col2.metric("Zone 1", len(df_agence[df_agence["Zone"] == "Zone 1"]))
col3.metric("Zone 2 & 3", len(df_agence[df_agence["Zone"] != "Zone 1"]))

# Tableau distances
st.write("### Distances moyennes par zone")
st.dataframe(
    df_agence.groupby("Zone")["Distance (km)"]
    .agg(["count", "mean"])
    .rename(columns={"count": "Nb localités", "mean": "Distance moyenne (km)"})
    .round(2)
)

# Carte interactive
st.subheader("Carte interactive des localités")
m = folium.Map(location=[coord_agence["Latitude_agence"], coord_agence["Longitude_agence"]], zoom_start=9)

# Ajouter le point noir de l'agence
folium.CircleMarker(
    location=[coord_agence["Latitude_agence"], coord_agence["Longitude_agence"]],
    radius=8,
    color="black",
    fill=True,
    fill_opacity=1.0,
    popup=f"Agence : {agence_selectionnee}"
).add_to(m)


colors = {"Zone 1": "green", "Zone 2": "orange", "Zone 3": "red"}

for _, row in df_agence.iterrows():
    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=5,
        color=colors.get(row["Zone"], "gray"),
        fill=True,
        fill_opacity=0.7,
        popup=f'{row["Commune"]} - {row["Zone"]} ({row["Distance (km)"]} km)'
    ).add_to(m)

st_folium(m, width=1100, height=600)

# Téléchargement
st.download_button(
    label="Télécharger les données de cette agence",
    data=df_agence.to_csv(index=False),
    file_name=f"{agence_selectionnee}_localites.csv",
    mime="text/csv"
)
