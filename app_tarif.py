import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(page_title="Normatrans - Zones et Tarifs", layout="wide")

st.title(" Normatrans - Zones et Tarifs de Livraison")

# Barre de navigation
menu = st.sidebar.radio(
    "Navigation",
    ["Analyse des Zones", "Calcul des Tarifs"],
    index=0
)

# =======================
# Partie 1 : Analyse des Zones
# =======================
if menu == "Analyse des Zones":
    st.header(" Analyse des zones de livraison")

    try:
        df = pd.read_csv("zones_final_localites1.csv", sep=";", encoding="utf-8")
        df.columns = df.columns.str.strip()
        st.success(" Données zones chargées avec succès")
    except Exception as e:
        st.error(f" Erreur de chargement : {e}")
        st.stop()

    required_cols = ["Commune", "Code agence", "Latitude", "Longitude", "Zone", "Distance (km)", "Latitude_agence", "Longitude_agence"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f" Colonnes manquantes : {missing_cols}")
        st.stop()

    df = df.dropna(subset=["Latitude", "Longitude"])

    agences = df["Code agence"].dropna().unique()
    agence_selectionnee = st.sidebar.selectbox(" Choisissez une agence :", agences)

    df_agence = df[df["Code agence"] == agence_selectionnee]
    coord_agence = df_agence[["Latitude_agence", "Longitude_agence"]].iloc[0]

    st.subheader(" Statistiques générales")
    col1, col2, col3 = st.columns(3)
    col1.metric("Nombre de localités", len(df_agence))
    col2.metric("Zone 1", len(df_agence[df_agence["Zone"] == "Zone 1"]))
    col3.metric("Zone 2 & 3", len(df_agence[df_agence["Zone"] != "Zone 1"]))

    fig = px.histogram(df_agence, x="Zone", color="Zone", title="📈 Répartition des localités par zone")
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

    # Marqueur agence
    folium.CircleMarker(
        location=[coord_agence["Latitude_agence"], coord_agence["Longitude_agence"]],
        radius=8,
        color="black",
        fill=True,
        fill_opacity=1.0,
        popup=f"Agence : {agence_selectionnee}"
    ).add_to(m)

    # Marqueurs localités
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

# =======================
# Partie 2 : Calcul des Tarifs
# =======================
elif menu == "Calcul des Tarifs":
    st.header("Calcul Global des Tarifs Pondérés par Zones")

    uploaded_file = st.file_uploader("📄 Uploader votre fichier de répartition (% d'expéditions)", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
            df = df.rename(columns={"% d'expéditions": "Pourcentage"})
            df["Pourcentage"] = df["Pourcentage"] / 100

            # Calcul global
            df_global = df.groupby("Zone")["Pourcentage"].sum().reset_index()
            df_global["Pourcentage"] = df_global["Pourcentage"] / df_global["Pourcentage"].sum()

            st.subheader("Choix des pondérations")
            coef_zone1 = st.slider("Coefficient Zone 1", min_value=0.5, max_value=5.0, value=1.0, step=0.1)
            coef_zone2 = st.slider("Coefficient Zone 2", min_value=0.5, max_value=5.0, value=2.0, step=0.1)
            coef_zone3 = st.slider("Coefficient Zone 3", min_value=0.5, max_value=5.0, value=3.0, step=0.1)

            ponderation = {"Zone 1": coef_zone1, "Zone 2": coef_zone2, "Zone 3": coef_zone3}
            df_global["Pondération"] = df_global["Zone"].map(ponderation)

            tarif_total = st.number_input("Tarif moyen souhaité (€)", min_value=1.0, max_value=1000.0, value=10.0, step=0.5)

            denominateur = (df_global["Pourcentage"] * df_global["Pondération"]).sum()
            base = tarif_total / denominateur
            df_global["Tarif par Zone (€)"] = (df_global["Pondération"] * base).round(2)

            st.success("Tarifs calculés avec succès")
            st.dataframe(df_global.style.format({"Pourcentage": "{:.2%}", "Tarif par Zone (€)": "{:.2f}€"}))

            csv = df_global.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Télécharger le fichier des tarifs",
                data=csv,
                file_name='tarifs_par_zone.csv',
                mime='text/csv'
            )

        except Exception as e:
            st.error(f"Erreur : {e}")

    else:
        st.info("Veuillez importer un fichier CSV pour démarrer.")

st.markdown("---")
st.caption("Normatrans © 2025 - Application développée pour zones & tarifs")
