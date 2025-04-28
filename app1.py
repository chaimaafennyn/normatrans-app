import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(layout="wide")

# Titre principal
st.markdown("""
<style>
.big-font {
font-size:25px !important;
color: #333;
text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">Bienvenue sur la plateforme Normatrans </p>', unsafe_allow_html=True)

# Menu principal
menu = st.sidebar.radio(
"Navigation",
["Analyse des Zones", "Calcul des Tarifs"],
index=0
)

# =========================================
# PARTIE 1 : Analyse des Zones
# =========================================
if menu == "Analyse des Zones":
st.header("Analyse des zones de livraison")

try:
df = pd.read_csv("zones_final_localites1.csv", sep=";", encoding="utf-8")
df.columns = df.columns.str.strip()
st.success("Données zones chargées avec succès")
except Exception as e:
st.error(f"Erreur de chargement : {e}")
st.stop()

required_cols = ["Commune", "Code agence", "Latitude", "Longitude", "Zone", "Distance (km)", "Latitude_agence", "Longitude_agence"]
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
st.error(f"Colonnes manquantes : {missing_cols}")
st.stop()

df = df.dropna(subset=["Latitude", "Longitude"])

agences = df["Code agence"].dropna().unique()
agence_selectionnee = st.sidebar.selectbox("Choisissez une agence :", agences)

df_agence = df[df["Code agence"] == agence_selectionnee]
coord_agence = df_agence[["Latitude_agence", "Longitude_agence"]].iloc[0]

st.subheader("Statistiques générales")
col1, col2, col3 = st.columns(3)
col1.metric("Nombre de localités", len(df_agence))
col2.metric("Zone 1", len(df_agence[df_agence["Zone"] == "Zone 1"]))
col3.metric("Zone 2 & 3", len(df_agence[df_agence["Zone"] != "Zone 1"]))

fig = px.histogram(df_agence, x="Zone", color="Zone", title="Répartition des localités par zone")
st.plotly_chart(fig)

st.write("### Distances moyennes par zone")
st.dataframe(
df_agence.groupby("Zone")["Distance (km)"]
.agg(["count", "mean"])
.rename(columns={"count": "Nb localités", "mean": "Distance moyenne (km)"})
.round(2)
)

st.subheader("Carte interactive des localités")
m = folium.Map(location=[coord_agence["Latitude_agence"], coord_agence["Longitude_agence"]], zoom_start=9)

folium.CircleMarker(
location=[coord_agence["Latitude_agence"], coord_agence["Longitude_agence"]],
radius=8,
color="black",
fill=True,
fill_opacity=1.0,
popup=f"Agence : {agence_selectionnee}"
).add_to(m)

colors = {"Zone 1": "green", "Zone 2": "orange", "Zone 3": "red"}
for _, row in df_agence.iterrows():
folium.CircleMarker(
location=[row["Latitude"], row["Longitude"]],
radius=5,
color=colors.get(row["Zone"], "gray"),
fill=True,
fill_opacity=0.7,
popup=f'{row["Commune"]} - {row["Zone"]} ({row["Distance (km)"]} km)'
).add_to(m)

st_folium(m, width=1100, height=600)

st.download_button(
label="Télécharger les données de cette agence",
data=df_agence.to_csv(index=False),
file_name=f"{agence_selectionnee}_localites.csv",
mime="text/csv"
)

# =========================================
# PARTIE 2 : Calcul des Tarifs
# =========================================
elif menu == "Calcul des Tarifs":
st.header("Calcul des tarifs pondérés")

uploaded_file = st.file_uploader("Choisissez le fichier de répartition d'expéditions par zone", type=["csv"])

if uploaded_file is not None:
df_tarif = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
df_tarif.columns = df_tarif.columns.str.strip()

methode = st.radio("Méthode de calcul :", ["Pondérée (Zone 1 < Zone 2 < Zone 3)", "Coefficient personnalisés"])

df_tarif = df_tarif.rename(columns={"% d'expéditions": "Pourcentage"})
df_tarif["Pourcentage"] = df_tarif["Pourcentage"] / 100

tarif_total = st.number_input("Tarif moyen global (ex: 10€)", value=10.0)

if methode == "Pondérée (Zone 1 < Zone 2 < Zone 3)":
def calcul_tarifs(agence_df):
pond = {"Zone 1": 1, "Zone 2": 2, "Zone 3": 3}
agence_df["Pondération"] = agence_df["Zone"].map(pond)
denom = (agence_df["Pourcentage"] * agence_df["Pondération"]).sum()
base = tarif_total / denom
agence_df["Tarif_zone (€)"] = (agence_df["Pondération"] * base).round(2)
return agence_df
else:
coef_zone1 = st.slider("Coefficient Zone 1", 1.0, 5.0, 1.0)
coef_zone2 = st.slider("Coefficient Zone 2", 1.0, 5.0, 2.0)
coef_zone3 = st.slider("Coefficient Zone 3", 1.0, 5.0, 3.0)

def calcul_tarifs(agence_df):
coefs = {"Zone 1": coef_zone1, "Zone 2": coef_zone2, "Zone 3": coef_zone3}
agence_df["Pondération"] = agence_df["Zone"].map(coefs)
denom = (agence_df["Pourcentage"] * agence_df["Pondération"]).sum()
base = tarif_total / denom
agence_df["Tarif_zone (€)"] = (agence_df["Pondération"] * base).round(2)
return agence_df

df_result = df_tarif.groupby("Code agence").apply(calcul_tarifs).reset_index(drop=True)

st.success("Tarifs calculés avec succès !")
st.dataframe(df_result)

st.download_button(
label="Télécharger le fichier avec tarifs",
data=df_result.to_csv(index=False),
file_name="tarifs_calcules.csv",
mime="text/csv"
)

# --- Footer + bouton reset
st.markdown("---")
st.caption("Normatrans_Fennyn © 2025")

if st.button("Revenir au menu principal"):
st.experimental_rerun()
