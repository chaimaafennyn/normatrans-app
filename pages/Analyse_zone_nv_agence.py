import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from folium.plugins import Search
from folium import FeatureGroup
from database import get_zones_nv_agence  # on utilise la BDD

# Initialiser show_content à False si pas déjà défini
if "show_content" not in st.session_state:
    st.session_state["show_content"] = False  # ← ou True selon ton besoin initial

# coordonnées fixes de la nouvelle agence
latitude_agence = 49.123456   # ← remplace par la vraie latitude
longitude_agence = -0.654321  # ← remplace par la vraie longitude

# Vérifier authentification
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🚫 Accès non autorisé. Veuillez vous connecter.")
    st.stop()

st.title("📍 Analyse des Zones - Nouvelle Agence")

# Masquer le contenu si demandé
if not st.session_state.get("show_content", True):
    st.info("ℹ️ Le contenu de cette page est actuellement masqué.")
    st.stop()

# Charger depuis Supabase
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
    "Distance_nouvelle_agence_km": "Distance (km)"
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

if "Distance (km)" in df.columns:
    st.write("### 📏 Distances moyennes par zone")
    st.dataframe(
        df.groupby("Zone")["Distance (km)"]
        .agg(["count", "mean"])
        .rename(columns={"count": "Nb localités", "mean": "Distance moyenne (km)"})
        .round(2)
    )
else:
    st.warning("⚠️ Colonne 'Distance (km)' absente des données.")

# 🗺️ Carte interactive
st.subheader("🗺️ Carte interactive des localités")

m = folium.Map(
    location=[latitude_agence, longitude_agence],
    zoom_start=9
)

folium.Marker(
    location=[latitude_agence, longitude_agence],
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
    data=df.to_csv(index=False, sep=";"),
    file_name="localites_nouvelle_agence.csv",
    mime='text/csv'
)
