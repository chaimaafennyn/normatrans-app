import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(page_title="Normatrans - Zones et Tarifs", layout="wide")

st.title("🚚 Normatrans - Zones et Tarifs de Livraison")

menu = st.sidebar.radio(
    "Navigation",
    ["Analyse des Zones", "Calcul des Tarifs", "Analyse des Expéditions", "Analyse des Poids", "Analyse des Tournées"],
    index=0
)


# =======================
# Partie 1 : Analyse des Zones
# =======================
if menu == "Analyse des Zones":
    st.header("🔎 Analyse des zones de livraison")

    # Partie fichier par défaut
    default_file = "zones_final_localites1.csv"

    uploaded_file = st.file_uploader("Uploader un autre fichier Zones (optionnel)", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
        st.success("✅ Nouveau fichier zones chargé !")
    else:
        df = pd.read_csv(default_file, sep=";", encoding="utf-8")
        st.info(f"📂 Fichier par défaut chargé : {default_file}")

    df.columns = df.columns.str.strip()

    required_cols = ["Commune", "Code agence", "Latitude", "Longitude", "Zone", "Distance (km)", "Latitude_agence", "Longitude_agence"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"❌ Colonnes manquantes : {missing_cols}")
        st.stop()

    df = df.dropna(subset=["Latitude", "Longitude"])

    agences = df["Code agence"].dropna().unique()
    agence_selectionnee = st.sidebar.selectbox("🏢 Choisissez une agence :", agences)

    df_agence = df[df["Code agence"] == agence_selectionnee]
    coord_agence = df_agence[["Latitude_agence", "Longitude_agence"]].iloc[0]

    st.subheader("📊 Statistiques générales")
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

# =======================
# Partie 2 : Calcul des Tarifs
# =======================
elif menu == "Calcul des Tarifs":
    st.header("💶 Calcul Global des Tarifs Pondérés par Zones")

    default_tarif_file = "repartition_par_zone.csv"

    uploaded_tarif = st.file_uploader("Uploader un autre fichier de répartition (optionnel)", type=["csv"])

    if uploaded_tarif is not None:
        df_tarif = pd.read_csv(uploaded_tarif, sep=";", encoding="utf-8")
        st.success("✅ Nouveau fichier de répartition chargé !")
    else:
        df_tarif = pd.read_csv(default_tarif_file, sep=";", encoding="utf-8")
        st.info(f"📂 Fichier de répartition par défaut chargé : {default_tarif_file}")

    df_tarif.columns = df_tarif.columns.str.strip()

    try:
        df_tarif = df_tarif.rename(columns={"% d'expéditions": "Pourcentage"})
        df_tarif["Pourcentage"] = df_tarif["Pourcentage"] / 100

        df_global = df_tarif.groupby("Zone")["Pourcentage"].sum().reset_index()
        df_global["Pourcentage"] = df_global["Pourcentage"] / df_global["Pourcentage"].sum()

        st.subheader("🎯 Coefficients de pondération")
        coef_zone1 = st.slider("Coefficient Zone 1", 0.5, 5.0, 1.0, step=0.1)
        coef_zone2 = st.slider("Coefficient Zone 2", 0.5, 5.0, 2.0, step=0.1)
        coef_zone3 = st.slider("Coefficient Zone 3", 0.5, 5.0, 3.0, step=0.1)

        ponderation = {"Zone 1": coef_zone1, "Zone 2": coef_zone2, "Zone 3": coef_zone3}
        df_global["Pondération"] = df_global["Zone"].map(ponderation)

        tarif_total = st.number_input("💰 Tarif moyen souhaité (€)", min_value=1.0, max_value=1000.0, value=10.0, step=0.5)

        denominateur = (df_global["Pourcentage"] * df_global["Pondération"]).sum()
        base = tarif_total / denominateur
        df_global["Tarif par Zone (€)"] = (df_global["Pondération"] * base).round(2)

        st.success("✅ Tarifs calculés avec succès")
        st.dataframe(df_global.style.format({"Pourcentage": "{:.2%}", "Tarif par Zone (€)": "{:.2f}€"}))

        csv = df_global.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger le fichier des tarifs",
            data=csv,
            file_name='tarifs_par_zone.csv',
            mime='text/csv'
        )

    except Exception as e:
        st.error(f"❌ Erreur : {e}")

# =======================
# Partie 3 : Analyse des Expéditions
# =======================
elif menu == "Analyse des Expéditions":
    st.header("📦 Analyse des Expéditions")

    # Uploader fichiers ou utiliser ceux par défaut
    default_global_file = "repartition_par_zone.csv"
    default_agence_file = "repartition_par_agence_et_zone.csv"

    uploaded_global = st.file_uploader("📁 Uploader le fichier global (optionnel)", type=["csv"])
    uploaded_agence = st.file_uploader("📁 Uploader le fichier par agence (optionnel)", type=["csv"])

    try:
        df_global = pd.read_csv(uploaded_global if uploaded_global else default_global_file, sep=";", encoding="utf-8")
        df_agence = pd.read_csv(uploaded_agence if uploaded_agence else default_agence_file, sep=";", encoding="utf-8")
        st.success("✅ Fichiers chargés avec succès")
    except Exception as e:
        st.error(f"Erreur de chargement des fichiers : {e}")
        st.stop()

    # Nettoyage
    df_global = df_global.rename(columns={"% d'expéditions": "Pourcentage"})
    df_agence = df_agence.rename(columns={"% d'expéditions": "Pourcentage"})

    for df in [df_global, df_agence]:
        df["Pourcentage"] = df["Pourcentage"].astype(str).str.replace(",", ".").astype(float)

    # Section 1 : Répartition Globale
    st.subheader("🌍 Répartition globale par zone")
    st.dataframe(df_global)
    st.bar_chart(df_global.set_index("Zone")["Pourcentage"])

    # Section 2 : Répartition par Agence
    st.subheader("🏢 Répartition par agence")
    agence_choisie = st.selectbox("Sélectionnez une agence :", df_agence["Code agence"].unique())
    df_agence_filtre = df_agence[df_agence["Code agence"] == agence_choisie]
    st.dataframe(df_agence_filtre)
    st.bar_chart(df_agence_filtre.set_index("Zone")["Pourcentage"])

    # Téléchargement des CSV
    st.download_button(
        label="📥 Télécharger la répartition globale",
        data=df_global.to_csv(index=False).encode("utf-8"),
        file_name="repartition_globale_par_zone.csv",
        mime="text/csv"
    )

    st.download_button(
        label=f"📥 Télécharger les données de l'agence {agence_choisie}",
        data=df_agence_filtre.to_csv(index=False).encode("utf-8"),
        file_name=f"repartition_{agence_choisie}.csv",
        mime="text/csv"
    )


# =======================
# Partie 4 : Analyse des Poids
# =======================
elif menu == "Analyse des Poids":
    st.header("⚖️ Analyse des Poids")

    # Fichier par défaut
    default_file = "analyse_poids_par_agence_et_zones.csv"

    # Upload facultatif
    uploaded_poids = st.file_uploader("Uploader un autre fichier des poids (optionnel)", type=["csv"])

    if uploaded_poids is not None:
        df_poids = pd.read_csv(uploaded_poids, sep=";", encoding="latin-1")
        st.success("✅ Fichier poids chargé avec succès !")
    else:
        df_poids = pd.read_csv(default_file, sep=";", encoding="latin-1")
        st.info(f"📂 Fichier par défaut utilisé : {default_file}")

    # Nettoyage des colonnes
    df_poids.columns = df_poids.columns.str.strip()
    # st.markdown("**Colonnes détectées :**")
    # st.write(df_poids.columns.tolist())

    try:
        # Remplacer les virgules par des points dans les colonnes numériques
        df_poids["Poids_total"] = df_poids["Poids_total"].astype(str).str.replace(",", ".").astype(float)
        df_poids["% Poids"] = df_poids["% Poids"].astype(str).str.replace(",", ".").astype(float)

        # Affichage tableau
        st.subheader("📋 Détail par agence et par zone")
        st.dataframe(df_poids)

        # Répartition globale par zone
        st.subheader("📊 Répartition globale des poids par zone")
        poids_global = df_poids.groupby("Zone")["Poids_total"].sum().reset_index()
        poids_global["% Poids"] = 100 * poids_global["Poids_total"] / poids_global["Poids_total"].sum()
        st.dataframe(poids_global.round(2))

        # Graphique camembert
        #st.subheader("🥧 Camembert des poids globaux par zone")
        fig = px.pie(poids_global, values="Poids_total", names="Zone", title="")
        st.plotly_chart(fig)

        # Export CSV
        st.download_button(
            label="📥 Télécharger les poids globaux",
            data=poids_global.to_csv(index=False).encode("utf-8"),
            file_name="repartition_poids_globale.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"❌ Erreur dans l’analyse des poids : {e}")

# =======================
# Partie 5 : Analyse des Tournées (avec marguerite)
# =======================
elif menu == "Analyse des Tournées":
    st.header("🔄 Analyse des Tournées de Livraison")

    default_tournee = "livraison_par_tournee.csv"
    default_agences = "coordonnees_agences_normatrans.csv"

    uploaded_tournee = st.file_uploader("Uploader un fichier de livraisons par tournée (optionnel)", type=["csv"])
    uploaded_agences = st.file_uploader("Uploader un fichier des coordonnées agences (optionnel)", type=["csv"])

    df_tournee = pd.read_csv(uploaded_tournee if uploaded_tournee else default_tournee, sep=";", encoding="latin-1")
    df_agences = pd.read_csv(uploaded_agences if uploaded_agences else default_agences, sep=";", encoding="utf-8")

    df_tournee.columns = df_tournee.columns.str.strip()
    df_agences.columns = df_agences.columns.str.strip()

    df_tournee["Poids"] = df_tournee["Poids"].astype(str).str.replace(",", ".").astype(float)
    df_tournee["UM"] = df_tournee["UM"].astype(str).str.replace(",", ".").astype(float)

    agence = st.selectbox("Choisissez une agence :", df_tournee["Code agence"].dropna().unique())
    df_ag = df_tournee[df_tournee["Code agence"] == agence]

    st.subheader("📋 Résumé par tournée")
    df_resume = df_ag.groupby("Tournee").agg(
        Nb_localités=("Commune", "nunique"),
        Total_poids=("Poids", "sum"),
        Total_UM=("UM", "sum")
    ).reset_index()
    st.dataframe(df_resume.round(2))

    st.subheader("🌼 Carte marguerite : Visualisation d'une tournée")
    tournee_select = st.selectbox("Choisissez une tournée :", df_ag["Tournee"].dropna().unique())
    df_map = df_ag[df_ag["Tournee"] == tournee_select]

    lat_ag = df_agences[df_agences["Code agence"] == agence]["Latitude"].values[0]
    lon_ag = df_agences[df_agences["Code agence"] == agence]["Longitude"].values[0]

    m = folium.Map(location=[lat_ag, lon_ag], zoom_start=9)

    # Marquer l'agence (centre de la marguerite)
    folium.Marker(
        location=[lat_ag, lon_ag],
        icon=folium.Icon(color="red"),
        popup=f"Agence {agence}"
    ).add_to(m)

    # Marquer les points de la tournée
    for _, row in df_map.iterrows():
        folium.PolyLine([[lat_ag, lon_ag], [row["Latitude"], row["Longitude"]]], color="gray", weight=1).add_to(m)
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=5,
            color="blue",
            fill=True,
            fill_opacity=0.7,
            popup=f"{row['Commune']}<br>Poids : {row['Poids']} kg<br>UM : {row['UM']}"
        ).add_to(m)

    st_folium(m, width=1000, height=600)

    st.download_button(
        label="📥 Télécharger les données de cette tournée",
        data=df_map.to_csv(index=False),
        file_name=f"tournee_{tournee_select}.csv",
        mime="text/csv"
    )
    
            
                
        
            
    
    



st.markdown("---")
st.caption("Normatrans © 2025 - Fennynch")
