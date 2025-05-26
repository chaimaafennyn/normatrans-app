# database.py

from sqlalchemy import create_engine
import pandas as pd
import streamlit as st

# Connexion à Supabase
def get_engine():
    db = st.secrets["database"]
    url = f"postgresql://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['dbname']}"
    return create_engine(url)

# Lecture des tables
def get_zones():
    engine = get_engine()
    return pd.read_sql("SELECT * FROM zones_localites", engine)

def get_tranches():
    engine = get_engine()
    return pd.read_sql("SELECT * FROM tranche_zone", engine)

# Exemple de fonction pour ajouter une ligne
def insert_tranche(tranche, zone, valeur):
    engine = get_engine()
    query = f"""
        INSERT INTO tranche_zone (tranche, zone, valeur)
        VALUES ('{tranche}', '{zone}', {valeur});
    """
    with engine.connect() as conn:
        conn.execute(query)
