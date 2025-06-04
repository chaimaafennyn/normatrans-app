import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
import plotly.express as px
from database import get_zones  # 🔁 ta fonction de récupération depuis Supabase

st.title("🧠 Analyse stratégique des localités")

# === Chargement des données
uploaded_file = st.file_uploader("📄 Upload un fichier CSV (optionnel)", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=";", encoding="latin1")
else:
    df = get_zones()

# === Nettoyage
df = df.rename(columns={
    "commune": "Commune",
    "distance_km": "Distance (km)",
    "code_agence": "Code agence",
    "latitude": "Latitude",
    "longitude": "Longitude"
})
df.columns = df.columns.str.strip()
df = df.dropna(subset=["Commune", "Distance (km)"])

# === Filtrage par agence
agences = df["Code agence"].dropna().unique()
agence_selectionnee = st.selectbox("🏢 Choisissez une agence :", ["Toutes"] + sorted(agences))

if agence_selectionnee != "Toutes":
    df = df[df["Code agence"] == agence_selectionnee]

# === Calcul des expéditions
df["Nb_expéditions"] = df.groupby("Commune")["Commune"].transform("count")
df_unique = df.drop_duplicates(subset=["Commune"]).copy()

# === Clustering
n_clusters = st.slider("🔢 Nombre de groupes à créer", 2, 6, 3)
X = df_unique[["Distance (km)", "Nb_expéditions"]]
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
df_unique["Cluster"] = kmeans.fit_predict(X)

# === Résultats de clustering
centroids = pd.DataFrame(kmeans.cluster_centers_, columns=["Distance (km)", "Nb_expéditions"])
centroids["Cluster"] = centroids.index.astype(str)

st.subheader("📍 Clustering : Distance vs Nb d’expéditions")
fig = px.scatter(
    df_unique,
    x="Distance (km)",
    y="Nb_expéditions",
    color=df_unique["Cluster"].astype(str),
    hover_data=["Commune", "Code agence"],
    title="Clustering des communes",
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

# === Carte (si coordonnées)
if "Latitude" in df_unique.columns and "Longitude" in df_unique.columns:
    st.subheader("🗺️ Carte géographique des clusters")
    fig_map = px.scatter_mapbox(
        df_unique,
        lat="Latitude",
        lon="Longitude",
        color=df_unique["Cluster"].astype(str),
        hover_name="Commune",
        zoom=5,
        mapbox_style="carto-positron"
    )
    st.plotly_chart(fig_map)

# === 📌 Analyse stratégique : localités éloignées
st.subheader("🚨 Localités à plus de 40 km de leur agence")
df_eloignees = df[df["Distance (km)"] > 40].sort_values(by="Distance (km)", ascending=False)
st.warning(f"{len(df_eloignees)} localités dépassent 40 km de distance.")
st.dataframe(df_eloignees[["Commune", "Code agence", "Distance (km)"]])

# === Suggestion
if len(df_eloignees) > 0:
    st.markdown("💡 **Suggestions possibles :**")
    st.markdown("- Étudier la faisabilité d’ouvrir une nouvelle agence dans ces zones.")
    st.markdown("- Réaffecter certaines localités à une agence plus proche si possible.")
    st.download_button(
        "📥 Télécharger la liste des localités éloignées",
        data=df_eloignees.to_csv(index=False),
        file_name="localites_eloignees.csv",
        mime="text/csv"
    )

# === Export général
with st.expander("📄 Voir les données de clustering complètes"):
    st.dataframe(df_unique.sort_values("Cluster"))

st.download_button(
    "💾 Télécharger les résultats complets",
    data=df_unique.to_csv(index=False).encode("utf-8"),
    file_name="resultats_clustering.csv",
    mime="text/csv"
)
