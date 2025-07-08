import streamlit as st
import pandas as pd
from math import radians, cos, sin, asin, sqrt
import plotly.express as px
import folium
from streamlit_folium import st_folium
from folium.plugins import Search
from folium import FeatureGroup

from database import (
    get_zones,
    get_agences,
    log_action,
)

# === Authentification requise ===
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🚫 Accès non autorisé. Veuillez vous connecter depuis la page principale.")
    st.stop()

st.title("🔎 Analyse des Zones de Livraison (avec recalcul)")

# === Charger données
df_localites = pd.DataFrame(get_zones())
df_agences = pd.DataFrame(get_agences())

# === Jointure localités + coordonnées agences
df = df_localites.merge(
    df_agences,
    left_on="code_agence",
    right_on="code_agence",
    suffixes=("", "_agence"),
    how="left"
)

if df["latitude_agence"].isna().any():
    st.error("⚠️ Certaines agences n'ont pas de coordonnées dans Supabase.")
    st.stop()

# === Fonction haversine
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    return R * c

# === Calculs distance et zone
df["distance_km"] = df.apply(
    lambda row: round(haversine(row["latitude"], row["longitude"], row["latitude_agence"], row["longitude_agence"]), 2),
    axis=1
)

df["zone"] = df["distance_km"].apply(
    lambda d: "Zone 1" if d <= 20 else ("Zone 2" if d <= 40 else "Zone 3")
)

# === Téléchargement CSV recalculé
st.download_button(
    label="📥 Télécharger fichier recalculé",
    data=df.to_csv(index=False, sep=";", encoding="utf-8"),
    file_name="localites_recalculées.csv",
    mime="text/csv"
)

# === Sélection agence
agences = df["code_agence"].dropna().unique()
agence_selectionnee = st.sidebar.selectbox("🏢 Choisissez une agence :", agences)
df_agence = df[df["code_agence"] == agence_selectionnee]
coord_agence = df_agence[["latitude_agence", "longitude_agence"]].iloc[0]

# === Statistiques
st.subheader("📊 Statistiques générales")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Nombre de localités", len(df_agence))
col2.metric("Zone 1", len(df_agence[df_agence["zone"] == "Zone 1"]))
col3.metric("Zone 2", len(df_agence[df_agence["zone"] == "Zone 2"]))
col4.metric("Zone 3", len(df_agence[df_agence["zone"] == "Zone 3"]))

fig = px.histogram(df_agence, x="zone", color="zone", title="📈 Répartition des localités par zone")
st.plotly_chart(fig)

st.write("### 📏 Distances moyennes par zone")
st.dataframe(
    df_agence.groupby("zone")["distance_km"]
    .agg(["count", "mean"])
    .rename(columns={"count": "Nb localités", "mean": "Distance moyenne (km)"})
    .round(2)
)

# === Carte
st.subheader("🗺️ Carte interactive des localités")

m = folium.Map(location=[coord_agence["latitude_agence"], coord_agence["longitude_agence"]], zoom_start=9)

folium.CircleMarker(
    location=[coord_agence["latitude_agence"], coord_agence["longitude_agence"]],
    radius=8, color="black", fill=True, fill_opacity=1.0,
    popup=f"Agence : {agence_selectionnee}"
).add_to(m)

localites_group = FeatureGroup(name="Localités")
colors = {"Zone 1": "green", "Zone 2": "orange", "Zone 3": "red"}

for _, row in df_agence.iterrows():
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=5,
        color=colors.get(row["zone"], "gray"),
        fill=True,
        fill_opacity=0.7,
        popup=row["commune"],
        tooltip=row["commune"]
    ).add_to(localites_group)

localites_group.add_to(m)

Search(
    layer=localites_group,
    search_label='commune',
    placeholder="🔍 Chercher une localité...",
    collapsed=False
).add_to(m)

st_folium(m, width=1100, height=600)
