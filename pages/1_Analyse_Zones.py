import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from math import radians, cos, sin, asin, sqrt
from folium.plugins import Search
from database import (
    get_zones,
    insert_localite,
    update_localite,
    delete_localite,
    log_action,
)

# === Authentification requise ===
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🚫 Accès non autorisé. Veuillez vous connecter depuis la page principale.")
    st.stop()

role = st.session_state.get("role", "utilisateur")

st.title("🔎 Analyse des Zones de Livraison")

uploaded_file = st.file_uploader("📄 Uploader un fichier CSV (optionnel)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=";", encoding="latin1")
    st.success("✅ Fichier CSV chargé")
else:
    df = get_zones()
    st.success("✅ Données chargées depuis Supabase")

# Renommer les colonnes pour correspondre à l'affichage
df = df.rename(columns={
    "commune": "Commune",
    "code_agence": "Code agence",
    "latitude": "Latitude",
    "longitude": "Longitude",
    "zone": "Zone",
    "distance_km": "Distance (km)",
    "latitude_agence": "Latitude_agence",
    "longitude_agence": "Longitude_agence"
})

df.columns = df.columns.str.strip()

# === Ajouter une localité (admin uniquement) ===
if role == "admin":
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        return R * c
    
    with st.form("ajout_localite"):
        commune = st.text_input("Commune")
        agences_existantes = df["Code agence"].dropna().unique()
        code_agence = st.selectbox("Code Agence", agences_existantes)
        latitude = st.number_input("Latitude", format="%.6f")
        longitude = st.number_input("Longitude", format="%.6f")
    
        # Obtenir coordonnées agence sélectionnée
        try:
            coord_ag = df[df["Code agence"] == code_agence][["Latitude_agence", "Longitude_agence"]].iloc[0]
            latitude_ag = coord_ag["Latitude_agence"]
            longitude_ag = coord_ag["Longitude_agence"]
    
            # IA : calculer la distance
            distance_calculee = round(haversine(latitude, longitude, latitude_ag, longitude_ag), 2)
            st.markdown(f"📏 **Distance calculée automatiquement : {distance_calculee} km**")
    
            # IA : suggestion zone automatique
            if distance_calculee <= 20:
                zone_suggeree = "Zone 1"
            elif distance_calculee <= 40:
                zone_suggeree = "Zone 2"
            else:
                zone_suggeree = "Zone 3"
    
            zone = st.selectbox("Zone", ["Zone 1", "Zone 2", "Zone 3"],
                                index=["Zone 1", "Zone 2", "Zone 3"].index(zone_suggeree))
    
        except IndexError:
            st.error("⚠️ Impossible de trouver les coordonnées de l'agence. Vérifiez les données.")
            st.stop()
    
        distance = st.number_input("Distance (km)", value=distance_calculee, format="%.2f")
        submitted = st.form_submit_button("Ajouter")
    
        if submitted:
            st.write("🔍 Données à insérer :", commune, zone, code_agence, latitude, longitude, latitude_ag, longitude_ag, distance)
            insert_localite(commune, zone, code_agence, latitude, longitude, latitude_ag, longitude_ag, distance)
            log_action(st.session_state["username"], "Ajout localité", f"{commune} | {zone} | {code_agence}")
            st.success(f"✅ Localité '{commune}' ajoutée avec distance {distance} km.")
            st.cache_data.clear()
            st.rerun()

else:
    st.info("🔒 Lecture seule : vous n'avez pas les droits pour modifier les données.")

# === Modifier ou Supprimer une localité (admin uniquement) ===
if role == "admin":
    st.subheader("🛠️ Modifier ou Supprimer une Localité")
    df_display = df[["id", "Commune", "Zone", "Code agence"]].astype(str)
    df_display["label"] = df_display["Commune"] + " | " + df_display["Zone"] + " | " + df_display["Code agence"]
    selected_row = st.selectbox("📍 Choisir une localité à modifier ou supprimer", df_display["label"])

    if selected_row:
        selected_id = int(df_display[df_display["label"] == selected_row]["id"].values[0])
        selected_data = df[df["id"] == selected_id].iloc[0]

        with st.form("modifier_supprimer"):
            commune = st.text_input("Commune", value=selected_data["Commune"])
            code_agence = st.text_input("Code Agence", value=selected_data["Code agence"])
            latitude = st.number_input("Latitude", value=selected_data["Latitude"], format="%.6f")
            longitude = st.number_input("Longitude", value=selected_data["Longitude"], format="%.6f")
            zone = st.selectbox("Zone", ["Zone 1", "Zone 2", "Zone 3"], index=["Zone 1", "Zone 2", "Zone 3"].index(selected_data["Zone"]))
            distance = st.number_input("Distance (km)", value=selected_data["Distance (km)"], format="%.2f")
            latitude_ag = st.number_input("Latitude Agence", value=selected_data["Latitude_agence"], format="%.6f")
            longitude_ag = st.number_input("Longitude Agence", value=selected_data["Longitude_agence"], format="%.6f")

            col1, col2 = st.columns(2)
            if col1.form_submit_button("💾 Modifier"):
                update_localite(selected_id, commune, zone, code_agence, latitude, longitude, latitude_ag, longitude_ag, distance)
                log_action(st.session_state["username"], "Modification localité", f"{commune} | {zone} | {code_agence}")
                st.success("✅ Localité mise à jour.")
                st.cache_data.clear()

            if col2.form_submit_button("🗑️ Supprimer"):
                delete_localite(selected_id)
                log_action(st.session_state["username"], "Suppression localité", f"{commune} | {zone} | {code_agence}")
                st.success("🗑️ Localité supprimée.")
                st.cache_data.clear()

# === Statistiques et carte ===
required_cols = ["Commune", "Code agence", "Latitude", "Longitude", "Zone", "Distance (km)", "Latitude_agence", "Longitude_agence"]
df = df.dropna(subset=["Latitude", "Longitude"])
agences = df["Code agence"].dropna().unique()
agence_selectionnee = st.sidebar.selectbox("🏢 Choisissez une agence :", agences)
df_agence = df[df["Code agence"] == agence_selectionnee]
coord_agence = df_agence[["Latitude_agence", "Longitude_agence"]].iloc[0]

st.subheader("📊 Statistiques générales")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Nombre de localités", len(df_agence))
col2.metric("Zone 1", len(df_agence[df_agence["Zone"] == "Zone 1"]))
col3.metric("Zone 2", len(df_agence[df_agence["Zone"] == "Zone 2"]))
col4.metric("Zone 3", len(df_agence[df_agence["Zone"] == "Zone 3"]))

fig = px.histogram(df_agence, x="Zone", color="Zone", title="📈 Répartition des localités par zone")
st.plotly_chart(fig)

st.write("### 📏 Distances moyennes par zone")
st.dataframe(
    df_agence.groupby("Zone")["Distance (km)"]
    .agg(["count", "mean"])
    .rename(columns={"count": "Nb localités", "mean": "Distance moyenne (km)"})
    .round(2)
)

st.subheader("🗺️ Carte interactive des localités")



m = folium.Map(location=[coord_agence["Latitude_agence"], coord_agence["Longitude_agence"]], zoom_start=9)
folium.CircleMarker(
    location=[coord_agence["Latitude_agence"], coord_agence["Longitude_agence"]],
    radius=8, color="black", fill=True, fill_opacity=1.0,
    popup=f"Agence : {agence_selectionnee}"
).add_to(m)

colors = {"Zone 1": "green", "Zone 2": "orange", "Zone 3": "red"}
for _, row in df_agence.iterrows():
    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=5, color=colors.get(row["Zone"], "gray"), fill=True, fill_opacity=0.7,
        popup=f'{row["Commune"]} - {row["Zone"]} ({row["Distance (km)"]} km)'
    ).add_to(m)

st_folium(m, width=1100, height=600)
st.download_button(
    label="📥 Télécharger les données de cette agence",
    data=df_agence.to_csv(index=False),
    file_name=f"{agence_selectionnee}_localites.csv",
    mime='text/csv'
)
