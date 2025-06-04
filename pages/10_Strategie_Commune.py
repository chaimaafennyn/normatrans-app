import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
import plotly.express as px
from database import get_zones  # Assure-toi que cette fonction fonctionne bien

st.set_page_config(page_title="Stratégie Agence", layout="wide")
st.title("🧠 Analyse Stratégique des Localités et Agences")

# === Chargement des données
uploaded_file = st.file_uploader("📄 Upload un fichier CSV (optionnel)", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=";", encoding="latin1")
else:
    df = get_zones()

# === Nettoyage et renommage
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

# === Ajout du nombre d’expéditions par commune
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

# === Carte géographique des clusters
if "Latitude" in df_unique.columns and "Longitude" in df_unique.columns:
    st.subheader("🗺️ Carte géographique des clusters")
    fig_map = px.scatter_mapbox(
        df_unique,
        lat="Latitude",
        lon="Longitude",
        color=df_unique["Cluster"].astype(str),
        hover_name="Commune",
        zoom=5,
        mapbox_style="carto-positron",
        title="📍 Carte des clusters des communes"
    )
    st.plotly_chart(fig_map)

# === Localités éloignées
st.subheader("🚨 Localités à plus de 40 km de leur agence")
df_eloignees = df[df["Distance (km)"] > 40].sort_values(by="Distance (km)", ascending=False)
st.warning(f"{len(df_eloignees)} localités dépassent 40 km.")

if not df_eloignees.empty:
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

# === Suggestion intelligente de nouvelle agence
st.subheader("🏗️ Suggestion intelligente d’ouverture d’agence")

seuil_distance = 40
seuil_nb_exp = 3

clusters_concernes = df_unique[
    (df_unique["Distance (km)"] > seuil_distance) & 
    (df_unique["Nb_expéditions"] > seuil_nb_exp)
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

from math import radians, cos, sin, asin, sqrt

# Fonction de calcul de distance (haversine)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # rayon de la Terre en km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    return R * c

st.subheader("🔁 Réaffectation des localités à une agence plus proche")

# Toutes les agences avec leurs coordonnées
agences_df = df.drop_duplicates(subset=["Code agence"])[["Code agence", "Latitude", "Longitude"]].dropna()

localites_reaffectables = []

for _, row in df_eloignees.iterrows():
    lat_loc, lon_loc = row["Latitude"], row["Longitude"]
    current_agence = row["Code agence"]

    # Calculer les distances à toutes les autres agences
    agences_df["distance"] = agences_df.apply(
        lambda x: haversine(lat_loc, lon_loc, x["Latitude"], x["Longitude"]), axis=1
    )
    agences_proches = agences_df.sort_values(by="distance")

    agence_plus_proche = agences_proches.iloc[0]
    if agence_plus_proche["Code agence"] != current_agence and agence_plus_proche["distance"] < row["Distance (km)"]:
        localites_reaffectables.append({
            "Commune": row["Commune"],
            "Agence actuelle": current_agence,
            "Distance actuelle (km)": round(row["Distance (km)"], 2),
            "Agence suggérée": agence_plus_proche["Code agence"],
            "Distance suggérée (km)": round(agence_plus_proche["distance"], 2)
        })

# Affichage
if localites_reaffectables:
    df_sugg = pd.DataFrame(localites_reaffectables)
    st.success("✅ Des agences plus proches sont disponibles pour certaines localités.")
    st.dataframe(df_sugg)
    st.download_button(
        "📥 Télécharger les suggestions de réaffectation",
        data=df_sugg.to_csv(index=False),
        file_name="suggestions_reaffectation.csv",
        mime="text/csv"
    )
else:
    st.info("Aucune réaffectation plus optimale détectée.")


st.download_button(
    "💾 Télécharger toutes les données (CSV)",
    data=df_unique.to_csv(index=False).encode("utf-8"),
    file_name="resultats_strategie_agence.csv",
    mime="text/csv"
)
