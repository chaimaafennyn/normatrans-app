import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st

# Connexion Supabase
def get_engine():
    db = st.secrets["database"]
    return create_engine(
        f"postgresql://{db.user}:{db.password}@{db.host}:{db.port}/{db.dbname}"
    )

# Chargement des données zones_localites
def get_zones():
    engine = get_engine()
    return pd.read_sql("SELECT * FROM zones_localites", engine)

# Chargement des données tranche_zone
def get_tranches():
    engine = get_engine()
    return pd.read_sql("SELECT * FROM tranche_zone", engine)

# Insérer une action dans la table logs
def log_action(username, action):
    engine = get_engine()
    with engine.connect() as conn:
        stmt = text("INSERT INTO logs (username, action) VALUES (:username, :action)")
        conn.execute(stmt, {"username": username, "action": action})

def insert_localite(commune, code_agence, zone, lat, lon, distance, lat_ag, lon_ag):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO zones_localites (commune, code_agence, zone, latitude, longitude, distance_km, latitude_agence, longitude_agence)
                VALUES (:commune, :code_agence, :zone, :lat, :lon, :distance, :lat_ag, :lon_ag)
            """),
            {
                "commune": commune,
                "code_agence": code_agence,
                "zone": zone,
                "lat": lat,
                "lon": lon,
                "distance": distance,
                "lat_ag": lat_ag,
                "lon_ag": lon_ag,
            }
        )
