import streamlit as st
from sqlalchemy import create_engine
import pandas as pd

# Identifiants (remplace par ceux de Supabase)
DB_USER = "postgres"
DB_PASSWORD = "Normatrans@2025"
DB_HOST = "db.rxtcigbzpbppqianbdcn.supabase.co"
DB_PORT = "5432"
DB_NAME = "postgres"

def get_engine():
    url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url)

def get_zones():
    engine = get_engine()
    query = "SELECT * FROM zones_localites"
    return pd.read_sql(query, engine)

