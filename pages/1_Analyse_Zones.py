import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
from sqlalchemy import create_engine

# ✅ Définir la config de page
st.set_page_config(page_title="Analyse des Zones", layout="wide")

# ✅ Convertir les secrets en dicts modifiables
credentials = dict(st.secrets["credentials"])
cookie = dict(st.secrets["cookie"])

# ✅ Hasher les mots de passe (obligatoire)
hashed_passwords = stauth.Hasher(credentials["passwords"]).generate()

authenticator = stauth.Authenticate(
    names=credentials["names"],
    usernames=credentials["usernames"],
    passwords=hashed_passwords,
    cookie_name="streamlit_app",
    key=cookie["key"],
    expiry_days=cookie["expiry_days"]
)

# ✅ Interface de connexion
name, authentication_status, username = authenticator.login("Connexion", "main")

if authentication_status is False:
    st.error("Nom d'utilisateur ou mot de passe incorrect.")
elif authentication_status is None:
    st.warning("Veuillez entrer vos identifiants.")
elif authentication_status:
    authenticator.logout("Se déconnecter", "sidebar")
    st.sidebar.success(f"Connecté en tant que {name}")

    # 🔐 Connexion base PostgreSQL Supabase
    db = st.secrets["database"]
    engine = create_engine(
        f"postgresql://{db.user}:{db.password}@{db.host}:{db.port}/{db.dbname}"
    )

    @st.cache_data
    def charger_donnees():
        return pd.read_sql("SELECT * FROM zones_localites", engine)

    df = charger_donnees()
    df = df.rename(columns={
        "commune": "Commune",
        "code_agence": "Code agence",
        "latitude": "Latitude",
        "longitude": "Longitude",
        "zone": "Zone",
        "distance_km": "Distance (km)",
        "latitude_agence": "Latitude_agence",
        "longitude_agence": "Longitude_agence"
    })

    required_cols = ["Commune", "Code agence", "Latitude", "Longitude", "Zone", "Distance (km)", "Latitude_agence", "Longitude_agence"]
    if any(col not in df.columns for col in required_cols):
        st.error("❌ Colonnes manquantes dans la base.")
        st.stop()

    df = df.dropna(subset=["Latitude", "Longitude"])

    st.subheader("📊 Statistiques générales")
    agences = df["Code agence"].dropna().unique()
    agence_selectionnee = st.selectbox("🏢 Choisissez une agence :", agences)
    df_agence = df[df["Code agence"] == agence_selectionnee]
    coord_agence = df_agence[["Latitude_agence", "Longitude_agence"]].iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Nombre de localités", len(df_agence))
    col2.metric("Zone 1", len(df_agence[df_agence["Zone"] == "Zone 1"]))
    col3.metric("Zone 2", len(df_agence[df_agence["Zone"] == "Zone 2"]))
    col4.metric("Zone 3", len(df_agence[df_agence["Zone"] == "Zone 3"]))

    fig = px.histogram(df_agence, x="Zone", color="Zone", title="📈 Répartition des localités par zone")
    st.plotly_chart(fig)

    st.write("### 📏 Distances moyennes par zone")
    st.dataframe(
        df_agence.groupby("Zone")["Distance (km)"]
        .agg(["count", "mean"])
        .rename(columns={"count": "Nb localités", "mean": "Distance moyenne (km)"})
        .round(2)
    )

    st.subheader("🗺️ Carte interactive des localités")
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
        label="📥 Télécharger les données de cette agence",
        data=df_agence.to_csv(index=False),
        file_name=f"{agence_selectionnee}_localites.csv",
        mime='text/csv'
    )
