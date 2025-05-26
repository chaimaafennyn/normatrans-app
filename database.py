import streamlit as st
from sqlalchemy import create_engine
import pandas as pd

db = st.secrets["database"]

def get_engine():
    url = f"postgresql://{db.user}:{db.password}@{db.host}:{db.port}/{db.dbname}"
    return create_engine(url)

def get_zones():
    engine = get_engine()
    query = "SELECT * FROM zones_localites"
    return pd.read_sql(query, engine)
