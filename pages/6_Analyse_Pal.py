import pandas as pd
import streamlit as st

st.header("📦 Analyse des Tranches de Palette (UM) par Zone")

uploaded_file = st.file_uploader("📄 Uploader le fichier des livraisons palettes (pal_tranche.csv)", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=";", encoding="latin1")
    st.success("✅ Fichier chargé")
else:
    st.stop()

df.columns = df.columns.str.strip()

# Nettoyage UM
df["UM"] = df["UM"].astype(str).str.replace(",", ".").astype(float)
df["Zone"] = df["Zone"].str.strip()
if "Code agence" in df.columns:
    df["Code agence"] = df["Code agence"].astype(str).str.strip()
