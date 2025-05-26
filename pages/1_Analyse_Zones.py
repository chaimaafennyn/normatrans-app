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


if st.session_state.get("role") == "admin":
    with st.expander("➕ Ajouter une nouvelle localité"):
        with st.form("ajout_formulaire"):
            commune = st.text_input("Commune")
            code_agence = st.selectbox("Code agence", df["Code agence"].unique())
            zone = st.selectbox("Zone", ["Zone 1", "Zone 2", "Zone 3"])
            lat = st.number_input("Latitude", format="%.6f")
            lon = st.number_input("Longitude", format="%.6f")
            distance = st.number_input("Distance (km)", format="%.2f")
            lat_ag = st.number_input("Latitude agence", format="%.6f")
            lon_ag = st.number_input("Longitude agence", format="%.6f")
            submit = st.form_submit_button("Ajouter")

            if submit:
                insert_localite(commune, code_agence, zone, lat, lon, distance, lat_ag, lon_ag)
                log_action(st.session_state["username"], f"Ajout de {commune}")
                st.success("✅ Localité ajoutée")
else:
    st.warning("🔒 Vous êtes en lecture seule (rôle utilisateur)")



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
