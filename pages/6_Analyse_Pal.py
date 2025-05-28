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

bins_um = [0, 0.5, 1, 2, 3, 4, 5, 10, float("inf")]
labels_um = ["0-0.5", "0.5-1", "1-2", "2-3", "3-4", "4-5", "5-10", ">10"]

df["Tranche UM"] = pd.cut(df["UM"], bins=bins_um, labels=labels_um, right=False)
df = df[df["Tranche UM"].notna()]

zones = df["Zone"].dropna().unique()
agences = df["Code agence"].dropna().unique() if "Code agence" in df.columns else []

col1, col2 = st.columns(2)
selected_zone = col1.selectbox("🌍 Filtrer par zone", ["Toutes"] + list(zones))
selected_agence = col2.selectbox("🏢 Filtrer par agence", ["Toutes"] + list(agences))

df_filtered = df.copy()
if selected_zone != "Toutes":
    df_filtered = df_filtered[df_filtered["Zone"] == selected_zone]
if selected_agence != "Toutes":
    df_filtered = df_filtered[df_filtered["Code agence"] == selected_agence]

st.markdown(f"🔎 **Filtres actifs :** Zone = `{selected_zone}` | Agence = `{selected_agence}`")

