import streamlit as st
import pandas as pd
import plotly.express as px

st.header("📦 Analyse des Tranches de Palette (UM) par Zone")

# Fichier à charger (depuis Supabase ou CSV)
uploaded_file = st.file_uploader("📄 Uploader le fichier des livraisons (pal_tranche.csv)", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=";", encoding="latin1")
    st.success("✅ Fichier chargé")
else:
    st.stop()

# Nettoyage
df.columns = df.columns.str.strip()
df["UM"] = df["UM"].astype(str).str.replace(",", ".").astype(float)
df["Zone"] = df["Zone"].str.strip()

# Définir les tranches de palette
bins = [0, 1, 2, 3, 4, 5, 6, float("inf")]
labels = ["1 palette", "2 palettes", "3 palettes", "4 palettes", "5 palettes", "6 palettes", "+6 palettes"]
df["Tranche_UM"] = pd.cut(df["UM"], bins=bins, labels=labels, right=True)
df = df[df["Tranche_UM"].notna()]

# Répartition par zone
st.subheader("📊 Répartition (%) des tranches de palettes par zone")
pivot = df.groupby(["Zone", "Tranche_UM"]).size().reset_index(name="Nb_exp")
totaux = pivot.groupby("Zone")["Nb_exp"].sum().reset_index(name="Total")
result = pd.merge(pivot, totaux, on="Zone")
result["Pourcentage"] = (result["Nb_exp"] / result["Total"] * 100).round(2)
tableau = result.pivot(index="Zone", columns="Tranche_UM", values="Pourcentage").fillna(0)
st.dataframe(tableau)

# Ajouter une ligne "Total"
total_global = df.groupby("Tranche_UM").size()
total_percent = (total_global / total_global.sum() * 100).round(2)
tableau.loc["Total"] = total_percent
st.dataframe(tableau)

# Graphique global
st.subheader("📈 Répartition globale des tranches de palette")
global_counts = df["Tranche_UM"].value_counts(normalize=True).sort_index() * 100
fig = px.bar(global_counts, x=global_counts.index, y=global_counts.values,
             labels={'x': "Tranche de palette", 'y': "Pourcentage"},
             title="Distribution globale des tranches de palettes")
st.plotly_chart(fig)
