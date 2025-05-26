import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
from database import get_zones


if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🚫 Accès non autorisé. Veuillez vous connecter depuis la page principale.")
    st.stop()

st.title("🔎 Analyse des Zones de Livraison")

from database import insert_zone, update_zone, delete_zone

st.markdown("---")
st.subheader("➕ Ajouter une nouvelle localité")

with st.form("add_form"):
    new_commune = st.text_input("Commune")
    new_zone = st.selectbox("Zone", ["Zone 1", "Zone 2", "Zone 3"])
    new_agence = st.selectbox("Code agence", sorted(df["Code agence"].unique()))
    new_lat = st.number_input("Latitude", format="%.6f")
    new_lon = st.number_input("Longitude", format="%.6f")
    new_lat_agence = st.number_input("Latitude agence", format="%.6f")
    new_lon_agence = st.number_input("Longitude agence", format="%.6f")
    new_dist = st.number_input("Distance (km)", format="%.2f")

    submitted = st.form_submit_button("Ajouter")
    if submitted:
        insert_zone(new_commune, new_zone, new_agence, new_lat, new_lon, new_lat_agence, new_lon_agence, new_dist)
        st.success("✅ Localité ajoutée avec succès.")
        st.experimental_rerun()

# === Modifier ou Supprimer ===
st.markdown("---")
st.subheader("🛠️ Modifier ou Supprimer une Localité")

df_display = df[["id", "Commune", "Zone", "Code agence"]].astype(str)
df_display["label"] = df_display["Commune"] + " | " + df_display["Zone"] + " | " + df_display["Code agence"]

selected = st.selectbox("📍 Sélectionner une localité", df_display["label"])
row_id = int(df_display[df_display["label"] == selected]["id"].values[0])
row_data = df[df["id"] == row_id].iloc[0]

with st.expander("✏️ Modifier cette localité"):
    col1, col2 = st.columns(2)
    commune_edit = col1.text_input("Commune", value=row_data["Commune"])
    zone_edit = col2.selectbox("Zone", ["Zone 1", "Zone 2", "Zone 3"], index=["Zone 1", "Zone 2", "Zone 3"].index(row_data["Zone"]))
    code_agence_edit = col1.text_input("Code agence", value=row_data["Code agence"])
    lat_edit = col2.number_input("Latitude", value=float(row_data["Latitude"]), format="%.6f")
    lon_edit = col1.number_input("Longitude", value=float(row_data["Longitude"]), format="%.6f")
    lat_agence_edit = col2.number_input("Latitude agence", value=float(row_data["Latitude_agence"]), format="%.6f")
    lon_agence_edit = col1.number_input("Longitude agence", value=float(row_data["Longitude_agence"]), format="%.6f")
    dist_edit = col2.number_input("Distance (km)", value=float(row_data["Distance (km)"]), format="%.2f")

    if st.button("✅ Enregistrer les modifications"):
        update_zone(row_id, commune_edit, zone_edit, code_agence_edit, lat_edit, lon_edit, lat_agence_edit, lon_agence_edit, dist_edit)
        st.success("✅ Localité mise à jour.")
        st.experimental_rerun()

    if st.button("🗑️ Supprimer cette localité"):
        delete_zone(row_id)
        st.warning("⚠️ Localité supprimée.")
        st.experimental_rerun()



uploaded_file = st.file_uploader("📄 Uploader un fichier CSV (optionnel)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=";", encoding="latin1")
    st.success("✅ Fichier CSV chargé")
else:   
    df = get_zones()
    st.success("✅ Données chargées depuis Supabase")



# Renommage des colonnes si nécessaire
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

    required_cols = ["Commune", "Code agence", "Latitude", "Longitude", "Zone", "Distance (km)", "Latitude_agence", "Longitude_agence"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"❌ Colonnes manquantes : {missing_cols}")
        st.stop()

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

    st.download_button(
        label="📥 Télécharger les données de cette agence",
        data=df_agence.to_csv(index=False),
        file_name=f"{agence_selectionnee}_localites.csv",
        mime='text/csv'
    )
