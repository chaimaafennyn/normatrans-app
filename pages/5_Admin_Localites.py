import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit_authenticator as stauth

# --- Authentification ---
credentials = st.secrets["credentials"]
cookie = st.secrets["cookie"]
authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name=cookie["name"],
    key=cookie["key"],
    cookie_expiry_days=cookie["expiry_days"]
)

name, auth_status, username = authenticator.login("🔐 Connexion admin", "main")
if not auth_status:
    st.stop()

# --- Config ---
st.set_page_config(page_title="Admin - Localités", layout="wide")
st.title("🔧 Administration des localités")

# --- Connexion à Supabase ---
db = st.secrets["database"]
engine = create_engine(f"postgresql://{db.user}:{db.password}@{db.host}:{db.port}/{db.dbname}")

# --- Lecture ---
df = pd.read_sql("SELECT * FROM zones_localites ORDER BY id", engine)
st.dataframe(df, use_container_width=True)

# --- Ajouter une nouvelle localité ---
st.subheader("➕ Ajouter une nouvelle localité")
with st.form("ajout_form"):
    col1, col2 = st.columns(2)
    with col1:
        commune = st.text_input("Commune")
        code_agence = st.text_input("Code agence")
        zone = st.selectbox("Zone", ["Zone 1", "Zone 2", "Zone 3"])
        cp = st.text_input("Code postal")
        code_insee = st.text_input("Code INSEE")
    with col2:
        latitude = st.number_input("Latitude", format="%.6f")
        longitude = st.number_input("Longitude", format="%.6f")
        distance = st.number_input("Distance (km)", format="%.2f")
        latitude_agence = st.number_input("Latitude agence", format="%.6f")
        longitude_agence = st.number_input("Longitude agence", format="%.6f")

    submitted = st.form_submit_button("Ajouter la localité")

    if submitted:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO zones_localites (
                    commune, code_agence, zone, cp, code_insee,
                    latitude, longitude, distance_km, latitude_agence, longitude_agence
                ) VALUES (
                    :commune, :code_agence, :zone, :cp, :code_insee,
                    :latitude, :longitude, :distance_km, :latitude_agence, :longitude_agence
                )
            """), {
                "commune": commune,
                "code_agence": code_agence,
                "zone": zone,
                "cp": cp,
                "code_insee": code_insee,
                "latitude": latitude,
                "longitude": longitude,
                "distance_km": distance,
                "latitude_agence": latitude_agence,
                "longitude_agence": longitude_agence
            })
        st.success("✅ Localité ajoutée avec succès.")
        st.rerun()

# --- Supprimer une ligne ---
st.subheader("🗑️ Supprimer une localité")
id_to_delete = st.number_input("ID à supprimer", min_value=1, step=1)
if st.button("Supprimer"):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM zones_localites WHERE id = :id"), {"id": id_to_delete})
    st.success(f"✅ Ligne ID {id_to_delete} supprimée.")
    st.rerun()
