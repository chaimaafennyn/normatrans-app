import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
import plotly.express as px
from database import get_zones  # ou ta propre fonction si tu charges depuis Supabase

st.title("🧠 Clustering des Communes (Distance vs Nombre d’expéditions)")

# === Chargement des données
uploaded_file = st.file_uploader("📄 Upload un fichier CSV (optionnel)", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=";", encoding="latin1")
else:
    df = get_zones()

# === Nettoyage & préparation
df = df.rename(columns={
    "commune": "Commune",
    "distance_km": "Distance (km)",
    "code_agence": "Code agence"
})
df.columns = df.columns.str.strip()
df = df.dropna(subset=["Commune", "Distance (km)"])
df["Nb_expéditions"] = df.groupby("Commune")["Commune"].transform("count")
df_unique = df.drop_duplicates(subset=["Commune"]).copy()

# === Choix du nombre de clusters
n_clusters = st.slider("🔢 Nombre de groupes à créer", 2, 6, 3)

# === Clustering avec KMeans
X = df_unique[["Distance (km)", "Nb_expéditions"]]
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
df_unique["Cluster"] = kmeans.fit_predict(X)

# === Affichage
st.subheader("📍 Résultat du clustering")
fig = px.scatter(
    df_unique,
    x="Distance (km)",
    y="Nb_expéditions",
    color=df_unique["Cluster"].astype(str),
    hover_data=["Commune"],
    title="Clusters des communes",
    labels={"Cluster": "Groupe"}
)
st.plotly_chart(fig)

# === Aperçu des données
with st.expander("📄 Voir les données de clustering"):
    st.dataframe(df_unique.sort_values("Cluster"))
