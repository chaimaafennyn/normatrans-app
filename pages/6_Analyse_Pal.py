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

st.subheader("📊 Répartition (%) des tranches UM par Zone")
pivot = df_filtered.groupby(["Zone", "Tranche UM"]).size().reset_index(name="Nb_exp")
total = pivot.groupby("Zone")["Nb_exp"].sum().reset_index(name="Total")
result = pd.merge(pivot, total, on="Zone")
result["Pourcentage"] = (result["Nb_exp"] / result["Total"] * 100).round(2)
tableau = result.pivot(index="Zone", columns="Tranche UM", values="Pourcentage").fillna(0)

st.subheader("📊 Répartition (%) des Zones par Tranche UM")
pivot_inv = df_filtered.groupby(["Tranche UM", "Zone"]).size().reset_index(name="Nb_exp")
total_inv = pivot_inv.groupby("Tranche UM")["Nb_exp"].sum().reset_index(name="Total")
result_inv = pd.merge(pivot_inv, total_inv, on="Tranche UM")
result_inv["Pourcentage"] = (result_inv["Nb_exp"] / result_inv["Total"] * 100).round(2)
tableau_inv = result_inv.pivot(index="Tranche UM", columns="Zone", values="Pourcentage").fillna(0)
st.dataframe(tableau_inv.T)



