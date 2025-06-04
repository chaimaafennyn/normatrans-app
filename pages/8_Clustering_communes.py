import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
import plotly.express as px
from database import get_zones

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

# === Filtrage par agence
agences = df_unique["Code agence"].dropna().unique()
agence_choisie = st.selectbox("🏢 Sélectionnez une agence :", agences)
df_unique = df_unique[df_unique["Code agence"] == agence_choisie]

# === Choix du nombre de clusters
n_clusters = st.slider("🔢 Nombre de groupes à créer", 2, 6, 3)

# === Clustering
X = df_unique[["Distance (km)", "Nb_expéditions"]]
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
df_unique["Cluster"] = kmeans.fit_predict(X)

# === Catégorisation métier
def categorize(row):
    if row["Distance (km)"] <= 20 and row["Nb_expéditions"] < 10:
        return "À dynamiser"
    elif row["Distance (km)"] > 20 and row["Nb_expéditions"] > 20:
        return "À surveiller"
    else:
        return "Normal"

df_unique["Catégorie"] = df_unique.apply(categorize, axis=1)

# === Visualisation
fig = px.scatter(
    df_unique,
    x="Distance (km)",
    y="Nb_expéditions",
    color="Cluster",
    hover_data=["Commune", "Catégorie"],
    title=f"Clusters des communes pour l'agence {agence_choisie}",
    labels={"Cluster": "Groupe"}
)
st.plotly_chart(fig)

# === Aperçu des données
with st.expander("📄 Voir les données de clustering"):
    st.dataframe(df_unique)

# === Téléchargement
csv = df_unique.to_csv(index=False).encode("utf-8")
st.download_button(
    label="💾 Télécharger les résultats (CSV)",
    data=csv,
    file_name=f"clustering_{agence_choisie}.csv",
    mime="text/csv"
)
