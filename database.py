import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd
from datetime import datetime


db = st.secrets["database"]

def get_engine():
    url = f"postgresql://{db.user}:{db.password}@{db.host}:{db.port}/{db.dbname}"
    return create_engine(url)

def get_zones():
    engine = get_engine()
    query = "SELECT * FROM zones_localites"
    return pd.read_sql(query, engine)

def get_tranches():
    engine = get_engine()
    query = "SELECT * FROM tranche_zone"
    return pd.read_sql(query, engine)

def get_palette():
    engine = get_engine()
    query = "SELECT * FROM pal_tranche"
    return pd.read_sql(query, engine)



def insert_localite(commune, zone, code_agence, lat, lon, lat_ag, lon_ag, distance):
    engine = get_engine()
    query = text("""
        INSERT INTO zones_localites (commune, zone, code_agence, latitude, longitude, latitude_agence, longitude_agence, distance_km)
        VALUES (:commune, :zone, :code_agence, :lat, :lon, :lat_ag, :lon_ag, :distance)
    """)
    with engine.begin() as conn:
        conn.execute(query, {
            "commune": commune,
            "zone": zone,
            "code_agence": code_agence,
            "lat": lat,
            "lon": lon,
            "lat_ag": lat_ag,
            "lon_ag": lon_ag,
            "distance": distance
        })

def update_localite(id, commune, zone, code_agence, lat, lon, lat_ag, lon_ag, distance):
    engine = get_engine()
    query = text("""
        UPDATE zones_localites
        SET commune = :commune,
            zone = :zone,
            code_agence = :code_agence,
            latitude = :lat,
            longitude = :lon,
            latitude_agence = :lat_ag,
            longitude_agence = :lon_ag,
            distance_km = :distance
        WHERE id = :id
    """)
    with engine.begin() as conn:
        conn.execute(query, {
            "id": id,
            "commune": commune,
            "zone": zone,
            "code_agence": code_agence,
            "lat": lat,
            "lon": lon,
            "lat_ag": lat_ag,
            "lon_ag": lon_ag,
            "distance": distance
        })

def delete_localite(id):
    engine = get_engine()
    query = text("DELETE FROM zones_localites WHERE id = :id")
    with engine.begin() as conn:
        conn.execute(query, {"id": id})


def get_local_time():
    # Utilise "Europe/Paris" ou "Africa/Casablanca" selon ta localisation
    tz = pytz.timezone("Europe/Paris")
    return datetime.now(tz)

def log_action(username, action, details):
    engine = get_engine()
    query = text("""
        INSERT INTO logs (username, action, details, timestamp)
        VALUES (:username, :action, :details, :timestamp)
    """)
    with engine.begin() as conn:
        conn.execute(query, {
            "username": username,
            "action": action,
            "details": details,
            "timestamp": get_local_time()  
        })
