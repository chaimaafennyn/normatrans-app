import streamlit as st
import pandas as pd
from math import radians, sin, cos, sqrt, asin
import folium
from streamlit_folium import st_folium
from folium import FeatureGroup
from folium.plugins import Search

from database import get_zones_nv_agence

st.title("🗺️ Carte des zones de la nouvelle agence")

# Charger les données
df = get_zones_nv_agence()

# Calculer la distance et la zone
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

df["distance_km"] = df.apply(
    lambda row: round(haversine(row["latitude"], row["longitude"],
                                row["latitude_agence"], row["longitude_agence"]), 2), axis=1
)

df["zone"] = df["distance_km"].apply(
    lambda d: "Zone 1" if d <= 20 else ("Zone 2" if d <= 40 else "Zone 3")
)

# Création de la carte centrée sur l'agence
latitude_agence = df["latitude_agence"].iloc[0]
longitude_agence = df["longitude_agence"].iloc[0]

m = folium.Map(location=[latitude_agence, longitude_agence], zoom_start=9)

# Marker pour l’agence
folium.Marker(
    location=[latitude_agence, longitude_agence],
    icon=folium.Icon(color="blue", icon="building", prefix="fa"),
    popup="Agence NT50X"
).add_to(m)

# Ajout des localités
colors = {"Zone 1": "green", "Zone 2": "orange", "Zone 3": "red"}
localites_group = FeatureGroup(name="Localités")

for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=5,
        color=colors.get(row["zone"], "gray"),
        fill=True,
        fill_opacity=0.7,
        popup=f"{row['commune']} - {row['zone']} ({row['distance_km']} km)",
        tooltip=row["commune"]
    ).add_to(localites_group)

localites_group.add_to(m)

# Barre de recherche
Search(
    layer=localites_group,
    search_label="commune",
    placeholder="🔍 Chercher une localité",
    collapsed=False
).add_to(m)

st_folium(m, width=1000, height=600)
