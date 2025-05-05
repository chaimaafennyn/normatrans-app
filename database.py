import streamlit as st
from sqlalchemy import create_engine
import pandas as pd

# Identifiants (remplace par ceux de Supabase)
DB_USER = "postgres.rxtcigbzpbppqianbdcn"   # 👈 Important
DB_PASSWORD = "chaimaafennyn"        # encode '@' en %40 si besoin
DB_HOST = "aws-0-eu-west-3.pooler.supabase.com"
DB_PORT = "6543"
DB_NAME = "postgres"

def get_engine():
    url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url)

def get_zones():
    engine = get_engine()
    query = "SELECT * FROM zones_localites"
    return pd.read_sql(query, engine)

from sqlalchemy import create_engine



