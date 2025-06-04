import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
import plotly.express as px
from database import get_zones  # Assure-toi que ta fonction existe

st.set_page_config(page_title="Stratégie Agence", layout="wide")

st.title("🧠 Analyse Stratégique des Localités et Agences")

# === Chargement
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

# === Nombre d’expéditions par commune
df["Nb_expéditions"] = df.groupby("Commune")["Commune"].transform("count")
df_unique = df.drop_duplicates(subset=["Commune"]).copy()

# === Clustering
n_clusters = st.slider("🔢 Nombre de clusters", 2, 6, 3)
X = df_unique[["Distance (km)", "Nb_expéditions"]]
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
df_unique["Cluster"] = kmeans.fit_predict(X)

# === Centroïdes
centroids = pd.DataFrame(kmeans.cluster_centers_, columns=["Distance (km)", "Nb_expéditions"])
centroids["Cluster"] = centroids.index.astype(str)

# === Graphe clustering
st.subheader("📍 Clustering : Distance vs Nombre d’expéditions")
fig = px.scatter(
    df_unique,
    x="Distance (km)",
    y="Nb_expéditions",
    color=df_unique["Cluster"].astype(str),
    hover_data=["Commune", "Code agence"],
    title="Visualisation des groupes de localités",
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

# === Carte (si données GPS)
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

# === Localités éloignées
st.subheader("🚨 Localités à plus de 40 km de leur agence")
df_eloignees = df[df["Distance (km)"] > 40].sort_values(by="Distance (km)", ascending=False)
st.warning(f"{len(df_eloignees)} localités dépassent 40 km.")

if len(df_eloignees) > 0:
    st.dataframe(df_eloignees[["Commune", "Code agence", "Distance (km)"]])
    st.markdown("💡 **Suggestions :**")
    st.markdown("- Réaffecter à une agence plus proche")
    st.markdown("- Étudier l’ouverture d’une agence secondaire")
    st.download_button(
        "📥 Télécharger les localités éloignées",
        data=df_eloignees.to_csv(index=False),
        file_name="localites_eloignees.csv",
        mime="text/csv"
    )

# === Analyse intelligente : suggérer nouvelle agence
st.subheader("🏗️ Suggestion intelligente d’ouverture d’agence")

seuil_distance = 40
seuil_nb_exp = 3  

clusters_concernes = df_unique[
    (df_unique["Distance (km)"] > seuil_distance) & (df_unique["Nb_expéditions"] > seuil_nb_exp)
]["Cluster"].unique()

if len(clusters_concernes) > 0:
    st.error("🚨 Des zones à fort volume et éloignées sont détectées.")
    for c in clusters_concernes:
        zone = df_unique[df_unique["Cluster"] == c]
        st.markdown(f"### 🔹 Cluster {c}")
        st.markdown(f"- 📍 Moyenne distance : {round(zone['Distance (km)'].mean(), 1)} km")
        st.markdown(f"- 📦 Total expéditions : {int(zone['Nb_expéditions'].sum())}")
        st.markdown("✅ **Suggestion : Étudier l’ouverture d’une agence dans cette zone.**")
else:
    st.success("✅ Aucun besoin critique détecté pour une nouvelle agence.")


# === Export complet
with st.expander("📄 Voir toutes les données de clustering"):
    st.dataframe(df_unique.sort_values("Cluster"))

st.download_button(
    "💾 Télécharger toutes les données (CSV)",
    data=df_unique.to_csv(index=False).encode("utf-8"),
    file_name="resultats_strategie_agence.csv",
    mime="text/csv"
)
