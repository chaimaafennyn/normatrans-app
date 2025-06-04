import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
import plotly.express as px
from database import get_zones

st.title("🧠 Clustering des Communes (Distance vs Expéditions)")

# Chargement CSV ou DB
uploaded_file = st.file_uploader("📄 Uploader un fichier CSV (optionnel)", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=";", encoding="latin1")
else:
    df = get_zones()

# Nettoyage
df = df.rename(columns={
    "commune": "Commune",
    "distance_km": "Distance (km)",
    "code_agence": "Code agence"
})
df.columns = df.columns.str.strip()
df = df.dropna(subset=["Commune", "Distance (km)"])
df["Nb_expéditions"] = df.groupby("Commune")["Commune"].transform("count")
df_unique = df.drop_duplicates(subset=["Commune"]).copy()

# === Filtrage par agence ===
agences = df_unique["Code agence"].dropna().unique().tolist()
selected_agence = st.selectbox("🏢 Filtrer par agence", ["Toutes"] + agences)

if selected_agence != "Toutes":
    df_unique = df_unique[df_unique["Code agence"] == selected_agence]

# Choix des clusters
n_clusters = st.slider("🔢 Nombre de groupes à créer", 2, 6, 3)

# Clustering
X = df_unique[["Distance (km)", "Nb_expéditions"]]
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
df_unique["Cluster"] = kmeans.fit_predict(X)

# Détection d'anomalies
def detect_anomalie(row):
    if row["Distance (km)"] < 15 and row["Nb_expéditions"] < 5:
        return "⚠️ Peu exploitée"
    elif row["Distance (km)"] > 45 and row["Nb_expéditions"] > 10:
        return "⚠️ Coût élevé"
    else:
        return ""

df_unique["Anomalie"] = df_unique.apply(detect_anomalie, axis=1)

# Centroïdes
centroids = pd.DataFrame(kmeans.cluster_centers_, columns=["Distance (km)", "Nb_expéditions"])
centroids["Cluster"] = centroids.index.astype(str)

# Graphique
st.subheader("📍 Clustering des communes")
fig = px.scatter(
    df_unique,
    x="Distance (km)",
    y="Nb_expéditions",
    color=df_unique["Cluster"].astype(str),
    hover_data=["Commune", "Anomalie"],
    symbol="Anomalie",
    title="📊 Regroupement par profil",
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

# Aperçu des données
with st.expander("📄 Voir les données"):
    st.dataframe(df_unique.sort_values("Cluster"))

# Téléchargement
csv = df_unique.to_csv(index=False).encode("utf-8")
st.download_button(
    label="💾 Télécharger les résultats (CSV)",
    data=csv,
    file_name="resultats_clustering.csv",
    mime="text/csv"
)
