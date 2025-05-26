import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import get_engine

st.set_page_config(page_title="🛠️ Gestion des Localités", layout="wide")

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🚫 Accès non autorisé. Veuillez vous connecter depuis la page principale.")
    st.stop()

st.title("🛠️ Gestion des Localités depuis Supabase")
engine = get_engine()

# --- Chargement des données ---
@st.cache_data(ttl=60)
def charger_data():
    with engine.connect() as conn:
        return pd.read_sql("SELECT * FROM zones_localites ORDER BY id", conn)

df = charger_data()

st.dataframe(df, use_container_width=True)

# --- Choix d'une ligne à modifier ou supprimer ---
st.subheader("✏️ Modifier ou Supprimer une ligne existante")
selected_id = st.selectbox("Sélectionnez l'ID de la ligne :", df["id"].tolist())
selected_row = df[df["id"] == selected_id].iloc[0]

# --- Formulaire commun pour édition et ajout ---
st.subheader("📋 Formulaire de gestion")
with st.form("formulaire"):
    commune = st.text_input("Commune", value=selected_row["commune"])
    code_agence = st.text_input("Code Agence", value=selected_row["code_agence"])
    latitude = st.number_input("Latitude", value=selected_row["latitude"])
    longitude = st.number_input("Longitude", value=selected_row["longitude"])
    zone = st.selectbox("Zone", ["Zone 1", "Zone 2", "Zone 3"], index=["Zone 1", "Zone 2", "Zone 3"].index(selected_row["zone"]))
    distance = st.number_input("Distance (km)", value=selected_row["distance_km"])
    lat_ag = st.number_input("Latitude Agence", value=selected_row["latitude_agence"])
    long_ag = st.number_input("Longitude Agence", value=selected_row["longitude_agence"])

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.form_submit_button("💾 Modifier"):
            with engine.begin() as conn:
                conn.execute(text("""
                    UPDATE zones_localites SET
                        commune = :commune,
                        code_agence = :code_agence,
                        latitude = :latitude,
                        longitude = :longitude,
                        zone = :zone,
                        distance_km = :distance,
                        latitude_agence = :lat_ag,
                        longitude_agence = :long_ag
                    WHERE id = :id
                """), {
                    "commune": commune,
                    "code_agence": code_agence,
                    "latitude": latitude,
                    "longitude": longitude,
                    "zone": zone,
                    "distance": distance,
                    "lat_ag": lat_ag,
                    "long_ag": long_ag,
                    "id": selected_id
                })
            st.success("✅ Localité modifiée.")
            st.rerun()

    with col2:
        if st.form_submit_button("➕ Ajouter comme nouvelle ligne"):
            with engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO zones_localites
                    (commune, code_agence, latitude, longitude, zone, distance_km, latitude_agence, longitude_agence)
                    VALUES (:commune, :code_agence, :latitude, :longitude, :zone, :distance, :lat_ag, :long_ag)
                """), {
                    "commune": commune,
                    "code_agence": code_agence,
                    "latitude": latitude,
                    "longitude": longitude,
                    "zone": zone,
                    "distance": distance,
                    "lat_ag": lat_ag,
                    "long_ag": long_ag
                })
            st.success("✅ Nouvelle localité ajoutée.")
            st.rerun()

    with col3:
        if st.form_submit_button("🗑️ Supprimer cette ligne"):
            with engine.begin() as conn:
                conn.execute(text("DELETE FROM zones_localites WHERE id = :id"), {"id": selected_id})
            st.warning("❌ Ligne supprimée.")
            st.rerun()

