import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from folium import FeatureGroup
from folium.plugins import Search

from database import get_zones_nv_agence, get_zones

st.title("📊 Comparaison Nouvelle Agence et Anciennes Agences")

# Charger les données
df_nv = get_zones_nv_agence()
df_old = get_zones()

if df_nv.empty or df_old.empty:
    st.error("❌ Données manquantes dans la base. Vérifiez vos tables.")
    st.stop()

# Nettoyage et renommage
df_nv = df_nv.rename(columns={
    "commune": "Commune", "latitude": "Latitude", "longitude": "Longitude",
    "zone": "Zone", "Distance_nouvelle_agence_km": "Distance (km)"
}).assign(Agence="Nouvelle Agence")

df_old = df_old.rename(columns={
    "commune": "Commune", "code_agence": "Code agence",
    "latitude": "Latitude", "longitude": "Longitude",
    "zone": "Zone", "distance_km": "Distance (km)"
}).dropna(subset=["Latitude", "Longitude"])

codes_agences = df_old["Code agence"].dropna().unique()

# Sélection des agences à comparer
selected_agences = st.multiselect(
    "🏢 Choisissez les agences à comparer",
    options=["Nouvelle Agence"] + list(codes_agences),
    default=["Nouvelle Agence"]
)

if not selected_agences:
    st.info("ℹ️ Sélectionnez au moins une agence pour afficher la comparaison.")
    st.stop()

# Fusionner les données sélectionnées
dfs = []

if "Nouvelle Agence" in selected_agences:
    dfs.append(df_nv)

for agence in selected_agences:
    if agence != "Nouvelle Agence":
        df_a = df_old[df_old["Code agence"] == agence].copy()
        df_a["Agence"] = agence
        dfs.append(df_a)

df_all = pd.concat(dfs)

# 📊 Stats générales
st.subheader("📊 Statistiques par agence")
stats = df_all.groupby("Agence").agg(
    Localités=("Commune", "count"),
    Zone_1=("Zone", lambda x: (x=="Zone 1").sum()),
    Zone_2=("Zone", lambda x: (x=="Zone 2").sum()),
    Zone_3=("Zone", lambda x: (x=="Zone 3").sum()),
    Distance_moyenne=("Distance (km)", "mean")
).round(2).reset_index()

st.dataframe(stats)

# 📈 Graphe
fig = px.histogram(
    df_all, x="Zone", color="Agence", barmode="group",
    title="Répartition des localités par zone et par agence"
)
st.plotly_chart(fig)

# 🗺️ Carte interactive
st.subheader("🗺️ Carte interactive")

m = folium.Map(location=[df_all["Latitude"].mean(), df_all["Longitude"].mean()], zoom_start=7)

colors_agences = {
    "Nouvelle Agence": "blue",
    codes_agences[0]: "green" if len(codes_agences) > 0 else "gray",
    codes_agences[1]: "orange" if len(codes_agences) > 1 else "gray"
}

groups = {}

for agence in selected_agences:
    groups[agence] = FeatureGroup(name=agence)
    subset = df_all[df_all["Agence"] == agence]
    for _, row in subset.iterrows():
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=4,
            color=colors_agences.get(agence, "gray"),
            fill=True,
            fill_opacity=0.7,
            popup=f"{row['Commune']} ({row['Zone']})",
            tooltip=row["Commune"]
        ).add_to(groups[agence])
    groups[agence].add_to(m)

Search(
    layer=list(groups.values())[0],
    search_label='Commune',
    placeholder="🔍 Chercher une localité...",
    collapsed=False
).add_to(m)

folium.LayerControl().add_to(m)

st_folium(m, width=1100, height=600)

# 📥 Télécharger les données
st.download_button(
    label="📥 Télécharger les données comparées",
    data=df_all.to_csv(index=False, sep=";"),
    file_name="comparaison_agences.csv",
    mime='text/csv'
)
