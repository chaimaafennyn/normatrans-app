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

