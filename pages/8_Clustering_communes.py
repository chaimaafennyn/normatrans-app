import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
import plotly.express as px
from database import get_zones  # ta fonction Supabase

st.title("🧠 Clustering des Communes (Distance vs Nombre d’expéditions)")

# === Chargement des données
uploaded_file = st.file_uploader("📄 Uploader un fichier CSV (optionnel)", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=";", encoding="latin1")
else:
    df = get_zones()

# === Filtrage par agence
if "code_agence" in df.columns:
    df = df.rename(columns={"code_agence": "Code agence"})
agences = df["Code agence"].dropna().unique()
agence_selectionnee = st.selectbox("🏢 Choisissez une agence :", ["Toutes"] + sorted(agences))

if agence_selectionnee != "Toutes":
    df = df[df["Code agence"] == agence_selectionnee]

# === Nettoyage & préparation
df = df.rename(columns={
    "commune": "Commune",
    "distance_km": "Distance (km)",
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

# === Détection d’anomalies (optionnel mais utile)
def detect_anomalie(row):
    if row["Distance (km)"] > 40 and row["Nb_expéditions"] < 3:
        return "📍 Lointaine & peu utilisée"
    elif row["Distance (km)"] < 10 and row["Nb_expéditions"] > 30:
        return "📍 Proche & très utilisée"
    return ""

df_unique["Anomalie"] = df_unique.apply(detect_anomalie, axis=1)

# === Récupération des centroïdes
centroids = pd.DataFrame(kmeans.cluster_centers_, columns=["Distance (km)", "Nb_expéditions"])
centroids["Cluster"] = centroids.index.astype(str)

# === Explication
with st.expander("ℹ️ À quoi sert ce clustering ?"):
    st.markdown("""
    Le clustering permet de **regrouper les communes** ayant des profils similaires :
    
    - 📏 Distance par rapport à l'agence
    - 📦 Fréquence d'expéditions
    
    Cela aide à :
    - Repenser la répartition des zones
    - Identifier les localités inefficaces
    - Optimiser les coûts logistiques
    """)

# === Affichage du graphique de clustering
st.subheader("📍 Résultat du clustering")
fig = px.scatter(
    df_unique,
    x="Distance (km)",
    y="Nb_expéditions",
    color=df_unique["Cluster"].astype(str),
    symbol="Anomalie",
    hover_data=["Commune", "Anomalie"],
    title="Clusters des communes",
    labels={"Cluster": "Groupe"}
)

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

# === Carte géographique (optionnelle)
if "latitude" in df_unique.columns and "longitude" in df_unique.columns:
    st.subheader("🗺️ Carte des clusters géographiques")
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
    
# === Filtrage interactif : afficher uniquement les anomalies
st.subheader("📋 Données de clustering")

afficher_anomalies = st.checkbox("🔍 Afficher uniquement les localités avec anomalies")

if afficher_anomalies:
    df_affichage = df_unique[df_unique["Anomalie"] != ""]
    st.warning("🧠 Vous affichez uniquement les communes avec anomalies détectées.")
else:
    df_affichage = df_unique

st.dataframe(df_affichage.sort_values("Cluster"))


# === Export CSV
csv = df_unique.to_csv(index=False).encode("utf-8")
st.download_button(
    label="💾 Télécharger les résultats (CSV)",
    data=csv,
    file_name="resultats_clustering.csv",
    mime="text/csv"
)
