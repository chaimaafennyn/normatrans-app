import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd

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

def insert_localite(data: dict):
    engine = get_engine()
    with engine.connect() as conn:
        insert_query = text("""
            INSERT INTO zones_localites (
                commune, code_agence, latitude, longitude, zone,
                distance_km, latitude_agence, longitude_agence
            ) VALUES (
                :commune, :code_agence, :latitude, :longitude, :zone,
                :distance_km, :latitude_agence, :longitude_agence
            )
        """)
        conn.execute(insert_query, data)
        conn.commit()
