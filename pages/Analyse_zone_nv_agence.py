import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from folium.plugins import Search
from folium import FeatureGroup

from database import get_zones_nv_agence  # Fonction qui lit la table Supabase zones_nv_agence

# Vérifier authentification
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🚫 Accès non autorisé. Veuillez vous connecter.")
    st.stop()

st.title("📍 Analyse des Zones - Nouvelle Agence")

# Charger les données
df = get_zones_nv_agence()
if df.empty:
    st.error("Aucune donnée disponible pour la nouvelle agence.")
    st.stop()

st.success("✅ Données chargées depuis Supabase")

# Nettoyer et renommer les colonnes
df = df.rename(columns={
    "commune": "Commune",
    "latitude": "Latitude",
    "longitude": "Longitude",
    "zone": "Zone",
    "distance_km": "Distance (km)",
    "latitude_agence": "Latitude_agence",
    "longitude_agence": "Longitude_agence"
}).dropna(subset=["Latitude", "Longitude"])

# 📊 Statistiques
st.subheader("📊 Statistiques générales")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Nombre de localités", len(df))
col2.metric("Zone 1", len(df[df["Zone"] == "Zone 1"]))
col3.metric("Zone 2", len(df[df["Zone"] == "Zone 2"]))
col4.metric("Zone 3", len(df[df["Zone"] == "Zone 3"]))

fig = px.histogram(
    df,
    x="Zone",
    color="Zone",
    title="📈 Répartition des localités par zone",
    category_orders={"Zone": ["Zone 1", "Zone 2", "Zone 3"]}
)
st.plotly_chart(fig)

st.write("### 📏 Distances moyennes par zone")
st.dataframe(
    df.groupby("Zone")["Distance (km)"]
    .agg(["count", "mean"])
    .rename(columns={"count": "Nb localités", "mean": "Distance moyenne (km)"})
    .round(2)
)

# 🗺️ Carte interactive
st.subheader("🗺️ Carte interactive des localités")

coord_agence = df[["Latitude_agence", "Longitude_agence"]].iloc[0]

m = folium.Map(
    location=[coord_agence["Latitude_agence"], coord_agence["Longitude_agence"]],
    zoom_start=9
)

folium.Marker(
    location=[coord_agence["Latitude_agence"], coord_agence["Longitude_agence"]],
    popup="Nouvelle Agence",
    icon=folium.Icon(color="blue", icon="building")
).add_to(m)

localites_group = FeatureGroup(name="Localités")

colors = {"Zone 1": "green", "Zone 2": "orange", "Zone 3": "red"}

for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=5,
        color=colors.get(row["Zone"], "gray"),
        fill=True,
        fill_opacity=0.7,
        popup=row["Commune"],
        tooltip=row["Commune"]
    ).add_to(localites_group)

localites_group.add_to(m)

Search(
    layer=localites_group,
    search_label='Commune',
    placeholder="🔍 Chercher une localité...",
    collapsed=False
).add_to(m)

st_folium(m, width=1100, height=600)

# 📥 Télécharger les données
st.download_button(
    label="📥 Télécharger les données",
    data=df.to_csv(index=False),
    file_name="localites_nouvelle_agence.csv",
    mime='text/csv'
)

