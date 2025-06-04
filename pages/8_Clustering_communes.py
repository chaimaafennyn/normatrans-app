import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
import plotly.express as px
from database import get_zones  # ou ta propre fonction Supabase

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

# === Récupération des centroïdes
centroids = pd.DataFrame(kmeans.cluster_centers_, columns=["Distance (km)", "Nb_expéditions"])
centroids["Cluster"] = centroids.index.astype(str)

# === Affichage du graphique de clustering
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
# Ajout des centroïdes au graphique
fig.add_scatter(
    x=centroids["Distance (km)"],
    y=centroids["Nb_expéditions"],
    mode="markers+text",
    marker=dict(size=12, symbol="x", color="black"),
    text=centroids["Cluster"],
    textposition="top center",
    name="Centroïdes"
)
st.plotly_chart(fig)

# === Carte géographique des communes (si coordonnées disponibles)
if "latitude" in df_unique.columns and "longitude" in df_unique.columns:
    st.subheader("🗺️ Clustering géographique des communes")
    fig_map = px.scatter_mapbox(
        df_unique,
        lat="latitude",
        lon="longitude",
        color=df_unique["Cluster"].astype(str),
        hover_name="Commune",
        zoom=5,
        mapbox_style="carto-positron"
    )
    st.plotly_chart(fig_map)

# === Aperçu des données
with st.expander("📄 Voir les données de clustering"):
    st.dataframe(df_unique.sort_values("Cluster"))

# === Téléchargement du résultat
csv = df_unique.to_csv(index=False).encode("utf-8")
st.download_button(
    label="💾 Télécharger les résultats (CSV)",
    data=csv,
    file_name="resultats_clustering.csv",
    mime="text/csv"
)
