# database.py
from sqlalchemy import create_engine
import pandas as pd

DB_USER = "postgres.rxtcigbzpbppqianbdcn"
DB_PASSWORD = "chaimaafennyn"
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
