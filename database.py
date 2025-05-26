import streamlit as st
from sqlalchemy import create_engine
import pandas as pd

def get_engine():
    db = st.secrets["database"]
    url = f"postgresql://{db.user}:{db.password}@{db.host}:{db.port}/{db.dbname}"
    return create_engine(url)

def get_zones():
    engine = get_engine()
    return pd.read_sql("SELECT * FROM zones_localites", engine)

def get_tranches():
    engine = get_engine()
    return pd.read_sql("SELECT * FROM tranche_zone", engine)

def log_action(username, action):
    engine = get_engine()
    query = f"""
        INSERT INTO logs (username, action)
        VALUES (%s, %s);
    """
    with engine.connect() as conn:
        conn.execute(query, (username, action))


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
