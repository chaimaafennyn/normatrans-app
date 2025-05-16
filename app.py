import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
 
st.set_page_config(page_title="Normatrans - Zones et Tarifs", layout="wide")

st.title("🚚 Normatrans - Zones et Tarifs de Livraison")

menu = st.sidebar.radio(
    "Navigation",
    ["Analyse des Zones", "Calcul des Tarifs",  "Analyse des Tranches de Poids", "Tarif par Zone et Tranche"],
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

    df_tournee = pd.read_csv(uploaded_tournee if uploaded_tournee else default_tournee, sep=";", encoding="latin1")
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


# =======================
# Partie 6 : Carte Marguerite (points uniquement)
# =======================
elif menu == "Marguerite par Agence":
    st.header("🌼 Marguerite des tournées - Vue par points")

    # Chargement des données optimisées
    default_file = "tournee_margueritte.csv"
    agence_coord_file = "coordonnees_agences_normatrans.csv"

    uploaded_tournee = st.file_uploader("Uploader un fichier de livraisons (optionnel)", type=["csv"])

    try:
        df = pd.read_csv(uploaded_tournee if uploaded_tournee else default_file, sep=";", encoding="latin1")
        df_agences = pd.read_csv(agence_coord_file, sep=";", encoding="utf-8")
        st.success("✅ Fichiers chargés")
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")
        st.stop()

    # Nettoyage
    df.columns = df.columns.str.strip()
    df["Tournee"] = df["Tournee"].astype(str)
    
    # Conversion sécurisée de Latitude et Longitude
    for col in ["Latitude", "Longitude"]:
        df[col] = df[col].astype(str).str.replace(",", ".").str.strip()
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    df = df.dropna(subset=["Latitude", "Longitude"])
    
    # Pour df_agences également :
    df_agences.columns = df_agences.columns.str.strip()
    for col in ["Latitude", "Longitude"]:
        df_agences[col] = df_agences[col].astype(str).str.replace(",", ".").str.strip()
        df_agences[col] = pd.to_numeric(df_agences[col], errors="coerce")
    
    df_agences = df_agences.dropna(subset=["Latitude", "Longitude"])


    agence_select = st.selectbox("Sélectionnez une agence :", df["Code agence"].dropna().unique())
    df_ag = df[df["Code agence"] == agence_select]

    coord_agence = df_agences[df_agences["Code agence"] == agence_select][["Latitude", "Longitude"]].iloc[0]

    st.subheader(f"🗺️ Carte des tournées - Agence {agence_select} (points uniquement)")

    import folium
    from streamlit_folium import st_folium
    import random

    m = folium.Map(location=[coord_agence["Latitude"], coord_agence["Longitude"]], zoom_start=10)

    # Marqueur de l’agence
    folium.Marker(
        [coord_agence["Latitude"], coord_agence["Longitude"]],
        popup=f"Agence {agence_select}",
        icon=folium.Icon(color="black", icon="building")
    ).add_to(m)

    # Couleurs par tournée
    tournees = df_ag["Tournee"].unique()
    colors = ["red", "blue", "green", "orange", "purple", "darkred", "cadetblue", "darkblue", "darkgreen",
              "darkpurple", "pink", "gray", "black", "lightblue", "beige", "lightgreen"]

    color_map = {t: colors[i % len(colors)] for i, t in enumerate(tournees)}

    for _, row in df_ag.iterrows():
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=4,
            color=color_map.get(row["Tournee"], "gray"),
            fill=True,
            fill_opacity=0.7,
            popup=f"{row['Commune']}<br>Tournée : {row['Tournee']}"
        ).add_to(m)

    st_folium(m, width=1000, height=600)

# =======================
# Partie 7 : Marguerite par Agence
# =======================
elif menu == "Marguerite par Agence2":
    st.header("🌸 Visualisation Marguerite - Tournées par Agence")

    import folium
    import numpy as np
    from shapely.geometry import MultiPoint
    from shapely.geometry.polygon import Polygon
    from streamlit_folium import st_folium
    import matplotlib.pyplot as plt
    from matplotlib import cm

    # Chargement des fichiers
    tournee_file = "tournee_margueritte.csv"
    agences_file = "coordonnees_agences_normatrans.csv"

    uploaded_tournee = st.file_uploader("Uploader un fichier de livraisons par tournée", type=["csv"])
    uploaded_agences = st.file_uploader("Uploader le fichier des coordonnées agences", type=["csv"])

    try:
        df_tournee = pd.read_csv(uploaded_tournee if uploaded_tournee else tournee_file, sep=";", encoding="latin1")
        df_agences = pd.read_csv(uploaded_agences if uploaded_agences else agences_file, sep=";", encoding="utf-8")
        st.success("✅ Données chargées avec succès.")
    except Exception as e:
        st.error(f"❌ Erreur : {e}")
        st.stop()

    # Nettoyage des colonnes
    df_tournee.columns = df_tournee.columns.str.strip()
    df_agences.columns = df_agences.columns.str.strip()
    
    # Nettoyage des données géographiques (remplacer virgules et valeurs vides)
    df_tournee["Latitude"] = df_tournee["Latitude"].astype(str).str.replace(",", ".").str.strip()
    df_tournee["Longitude"] = df_tournee["Longitude"].astype(str).str.replace(",", ".").str.strip()
    
    # Filtrer les lignes valides
    df_tournee = df_tournee[df_tournee["Latitude"].str.match(r'^-?\d+(\.\d+)?$')]
    df_tournee = df_tournee[df_tournee["Longitude"].str.match(r'^-?\d+(\.\d+)?$')]
    
    # Conversion après vérification
    df_tournee["Latitude"] = df_tournee["Latitude"].astype(float)
    df_tournee["Longitude"] = df_tournee["Longitude"].astype(float)
    
    # Pour les agences aussi
    df_agences["Latitude"] = pd.to_numeric(df_agences["Latitude"], errors="coerce")
    df_agences["Longitude"] = pd.to_numeric(df_agences["Longitude"], errors="coerce")
    df_agences = df_agences.dropna(subset=["Latitude", "Longitude"])


    

    # Sélection de l’agence
    agence_select = st.selectbox("Choisissez une agence :", df_tournee["Code agence"].dropna().unique())
    df_ag = df_tournee[df_tournee["Code agence"] == agence_select]

    if agence_select not in df_agences["Code agence"].values:
        st.error("❌ Coordonnées manquantes pour cette agence.")
        st.stop()

    coord = df_agences[df_agences["Code agence"] == agence_select][["Latitude", "Longitude"]].iloc[0]

    # Carte centrée sur l’agence
    m = folium.Map(location=[coord["Latitude"], coord["Longitude"]], zoom_start=10)
    folium.Marker([coord["Latitude"], coord["Longitude"]],
                  popup=f"Agence {agence_select}",
                  icon=folium.Icon(color="black", icon="building")).add_to(m)

    # Couleurs uniques
    tournees = df_ag["Tournee"].unique()
    colormap = cm.get_cmap("tab20", len(tournees))
    colors = [f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}" for r, g, b, _ in colormap(np.linspace(0, 1, len(tournees)))]

    # Tracer les polygones convexes des tournées
    for i, (tournee, group) in enumerate(df_ag.groupby("Tournee")):
        color = colors[i % len(colors)]
        points = list(zip(group["Latitude"], group["Longitude"]))
        if len(points) >= 3:
            hull = MultiPoint(points).convex_hull
            if isinstance(hull, Polygon):
                folium.Polygon(
                    locations=[[lat, lon] for lat, lon in hull.exterior.coords],
                    color=color,
                    fill=True,
                    fill_opacity=0.4,
                    tooltip=f"Tournée {tournee}"
                ).add_to(m)

        # Points des localités
        for _, row in group.iterrows():
            folium.CircleMarker(
                location=[row["Latitude"], row["Longitude"]],
                radius=3,
                color=color,
                fill=True,
                fill_opacity=1,
                popup=f"{row['Commune']} (Tournée {tournee})"
            ).add_to(m)

    st.subheader("🗺️ Carte des Tournées")
    st_folium(m, width=1000, height=650)

# =======================
# Partie 8 : Carte des Tournées (points uniquement)
# =======================
elif menu == "Analyse des tournees2":
    st.header("📍 Carte des Tournées (Points par agence)")

    # Fichiers par défaut
    default_tournee_file = "tournee_margueritte.csv"

    uploaded_tournee_file = st.file_uploader("Uploader un fichier des tournées optimisées (optionnel)", type=["csv"])

    if uploaded_tournee_file:
        df_tournee = pd.read_csv(uploaded_tournee_file, sep=";", encoding="utf-8")
        st.success("✅ Fichier de tournée optimisée chargé.")
    else:
        df_tournee = pd.read_csv(default_tournee_file, sep=";", encoding="utf-8")
        st.info(f"📂 Fichier par défaut utilisé : {default_tournee_file}")

    df_tournee.columns = df_tournee.columns.str.strip()

    try:
        df_tournee["Latitude"] = df_tournee["Latitude"].astype(float)
        df_tournee["Longitude"] = df_tournee["Longitude"].astype(float)
    except:
        st.error("❌ Erreur dans la conversion des coordonnées.")
        st.stop()

    agence_select = st.selectbox("Choisissez une agence :", df_tournee["Code agence"].dropna().unique())
    df_ag = df_tournee[df_tournee["Code agence"] == agence_select]

    st.subheader(f"🗺️ Carte des tournées (agence {agence_select})")

    import folium
    from streamlit_folium import st_folium

    m = folium.Map(location=[df_ag["Latitude"].mean(), df_ag["Longitude"].mean()], zoom_start=9)

    for _, row in df_ag.iterrows():
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=4,
            color="blue",
            fill=True,
            fill_opacity=0.6,
            popup=f"""
                <b>Commune :</b> {row['Commune']}<br>
                <b>Tournée(s) :</b> {row['Tournee']}<br>
                <b>Poids :</b> {row['Poids']} kg<br>
                <b>UM :</b> {row['UM']}
            """,
        ).add_to(m)

    st_folium(m, width=1000, height=600)

    st.download_button(
        label="📥 Télécharger les données filtrées",
        data=df_ag.to_csv(index=False),
        file_name=f"tournée_points_{agence_select}.csv",
        mime="text/csv"
    )
# =======================
# Partie 9 : Analyse des Tranches de Poids
# =======================
elif menu == "Analyse des Tranches de Poids":
    st.header("📦 Analyse des Tranches de Poids par Zone")

    uploaded_file = st.file_uploader("📄 Uploader le fichier des livraisons (livraison_par_tournee.csv)", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file, sep=";", encoding="latin1")
        st.success("✅ Fichier chargé")
    else:
        default_file = "livraison_par_tournee.csv"
        try:
            df = pd.read_csv(default_file, sep=";", encoding="latin1")
            st.info(f"📂 Fichier par défaut utilisé : {default_file}")
        except:
            st.error("❌ Fichier introuvable")
            st.stop()

    df.columns = df.columns.str.strip()
    df["Poids"] = df["Poids"].astype(str).str.replace(",", ".").astype(float)
    df["Zone"] = df["Zone"].str.strip()
    if "UM" in df.columns:
        df["UM"] = df["UM"].astype(str).str.replace(",", ".").astype(float)

    # Tranches de poids
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 500, 700, 1000, 1500, 2000, 3000, float('inf')]
    labels = [
        "0-10kg", "10-20kg", "20-30kg", "30-40kg", "40-50kg",
        "50-60kg", "60-70kg", "70-80kg", "80-90kg", "90-100kg",
        "100-200kg", "200-300kg", "300-500kg", "500-700kg",
        "700-1000kg", "1000-1500kg", "1500-2000kg", "2000-3000kg", ">3000kg"
    ]
    df["Tranche"] = pd.cut(df["Poids"], bins=bins, labels=labels, right=False)
    df = df[df["Tranche"].notna()]

    # === Filtres optionnels ===
    zones = df["Zone"].dropna().unique()
    agences = df["Code agence"].dropna().unique() if "Code agence" in df.columns else []

    col1, col2 = st.columns(2)
    selected_zone = col1.selectbox("🌟 Filtrer par zone", ["Toutes"] + list(zones))
    selected_agence = col2.selectbox(
        "🏢 Filtrer par agence",
        ["Toutes"] + list(agences) if len(agences) > 0 else ["Aucune"]
    )

    df_filtered = df.copy()
    if selected_zone != "Toutes":
        df_filtered = df_filtered[df_filtered["Zone"] == selected_zone]
    if selected_agence != "Toutes" and "Code agence" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["Code agence"] == selected_agence]

    st.markdown(f"🔎 **Filtres actifs :** Zone = `{selected_zone}` | Agence = `{selected_agence}`")

    # === Tranches par zone ===
    st.subheader("📊 Répartition (%) des tranches de poids par zone")
    pivot = df_filtered.groupby(["Zone", "Tranche"]).size().reset_index(name="Nb_exp")
    totaux = pivot.groupby("Zone")["Nb_exp"].sum().reset_index(name="Total")
    result = pd.merge(pivot, totaux, on="Zone")
    result["Pourcentage"] = (result["Nb_exp"] / result["Total"] * 100).round(2)
    tableau = result.pivot(index="Zone", columns="Tranche", values="Pourcentage").fillna(0)
    st.dataframe(tableau)

    st.download_button(
        "📅 Télécharger les pourcentages par tranche et zone",
        data=tableau.to_csv().encode("utf-8"),
        file_name="repartition_tranches_par_zone.csv",
        mime="text/csv"
    )

    # === Détail global
    st.subheader("📋 Détail global par agence, zone et commune")
    group_cols = ["Zone", "Commune"]
    if "Code agence" in df_filtered.columns:
        group_cols.insert(0, "Code agence")

    aggregations = {
        "Poids": ["count", "sum"],
    }
    if "UM" in df_filtered.columns:
        aggregations["UM"] = "sum"

    detail = df_filtered.groupby(group_cols).agg(aggregations)
    detail.columns = ["Nb_expéditions", "Poids_total"] + (["UM_total"] if "UM" in df_filtered.columns else [])
    detail = detail.reset_index().round(2)

    st.dataframe(detail)

    # === Top 100 communes
    if "Commune" in detail.columns:
        st.subheader("🏆 Top 100 communes avec le plus d'expéditions")
        top_communes = detail.groupby("Commune")["Nb_expéditions"].sum().nlargest(100).reset_index()
        st.bar_chart(top_communes.set_index("Commune")["Nb_expéditions"])

    st.download_button(
        "📅 Télécharger le tableau complet",
        data=detail.to_csv(index=False).encode("utf-8"),
        file_name="detail_agence_zone_commune.csv",
        mime="text/csv"
    )

    # === Statistiques globales Zone / Agence
    if "UM" in df_filtered.columns:
        st.subheader("⚖️ Statistiques Poids / UM / Exp par Zone")
        stats_zone = df_filtered.groupby("Zone").agg(
            Exp_total=("Poids", "count"),
            Poids_total=("Poids", "sum"),
            UM_total=("UM", "sum"),
            Poids_moyen=("Poids", "mean"),
            UM_moyenne=("UM", "mean"),
            UM_par_kg=("UM", lambda x: x.sum() / df_filtered.loc[x.index, "Poids"].sum())
        ).round(2)
        st.dataframe(stats_zone)

        if "Code agence" in df_filtered.columns:
            st.subheader("🏢 Statistiques Poids / UM / Exp par Agence")
            stats_agence = df_filtered.groupby("Code agence").agg(
                Exp_total=("Poids", "count"),
                Poids_total=("Poids", "sum"),
                UM_total=("UM", "sum"),
                Poids_moyen=("Poids", "mean"),
                UM_moyenne=("UM", "mean"),
                UM_par_kg=("UM", lambda x: x.sum() / df_filtered.loc[x.index, "Poids"].sum())
            ).round(2)
            st.dataframe(stats_agence)

    # === Graphiques camembert globaux
    st.subheader("🥧 Graphiques de répartition globaux")

    # Tranches
    pie_tranches = df_filtered["Tranche"].value_counts().reset_index()
    pie_tranches.columns = ["Tranche", "Nb_exp"]
    fig = px.pie(pie_tranches, names="Tranche", values="Nb_exp", title="Répartition des tranches de poids")
    st.plotly_chart(fig)

    # Expéditions par Zone
    zone_exp = df_filtered["Zone"].value_counts().reset_index()
    zone_exp.columns = ["Zone", "Nb_exp"]
    fig = px.pie(zone_exp, names="Zone", values="Nb_exp", title="Expéditions par Zone")
    st.plotly_chart(fig)

    # Expéditions par Agence
    if "Code agence" in df_filtered.columns:
        agence_exp = df_filtered["Code agence"].value_counts().reset_index()
        agence_exp.columns = ["Code agence", "Nb_exp"]
        fig = px.pie(agence_exp, names="Code agence", values="Nb_exp", title="Expéditions par Agence")
        st.plotly_chart(fig)

    # Poids total par Zone
    zone_poids = df_filtered.groupby("Zone")["Poids"].sum().reset_index()
    fig = px.pie(zone_poids, names="Zone", values="Poids", title="Poids total (kg) par Zone")
    st.plotly_chart(fig)

    # Poids total par Agence
    if "Code agence" in df_filtered.columns:
        poids_agence = df_filtered.groupby("Code agence")["Poids"].sum().reset_index()
        fig = px.pie(poids_agence, names="Code agence", values="Poids", title="Poids total (kg) par Agence")
        st.plotly_chart(fig)

    # UM total par Zone
    if "UM" in df_filtered.columns:
        zone_um = df_filtered.groupby("Zone")["UM"].sum().reset_index()
        fig = px.pie(zone_um, names="Zone", values="UM", title="UM total par Zone")
        st.plotly_chart(fig)

    # UM total par Agence
    if "UM" in df_filtered.columns and "Code agence" in df_filtered.columns:
        um_agence = df_filtered.groupby("Code agence")["UM"].sum().reset_index()
        fig = px.pie(um_agence, names="Code agence", values="UM", title="UM total par Agence")
        st.plotly_chart(fig)


# =======================
# Partie 10 : Tarification fixe par tranche modulée par zone
# =======================
elif menu == "Tarif par Zone et Tranche":
    st.header("💶 Tarification fixe par Tranche, modulée par Zone")

    uploaded_file = st.file_uploader("📤 Uploader le fichier des livraisons (livraison_par_tournee.csv)", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file, sep=";", encoding="latin1")
        st.success("✅ Fichier chargé avec succès")
    else:
        default_file = "livraison_par_tournee.csv"
        try:
            df = pd.read_csv(default_file, sep=";", encoding="latin1")
            st.info(f"📂 Fichier par défaut utilisé : {default_file}")
        except:
            st.error("❌ Fichier introuvable")
            st.stop()

    df.columns = df.columns.str.strip()
    df["Poids"] = df["Poids"].astype(str).str.replace(",", ".").astype(float)
    df["Zone"] = df["Zone"].str.strip()

    bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 500, 700, 1000, 1500, 2000, 3000, float('inf')]
    labels = [
        "0-10kg", "10-20kg", "20-30kg", "30-40kg", "40-50kg",
        "50-60kg", "60-70kg", "70-80kg", "80-90kg", "90-100kg",
        "100-200kg", "200-300kg", "300-500kg", "500-700kg",
        "700-1000kg", "1000-1500kg", "1500-2000kg", "2000-3000kg", ">3000kg"
    ]
    df["Tranche"] = pd.cut(df["Poids"], bins=bins, labels=labels, right=False)
    df = df[df["Tranche"].notna()]

    # === Définir les tarifs fixes par tranche ===
    tarif_base = {
        "0-10kg": 8.58, "10-20kg": 8.95, "20-30kg": 9.43, "30-40kg": 9.79,
        "40-50kg": 10.52, "50-60kg": 10.88, "60-70kg": 11.73, "70-80kg": 12.09,
        "80-90kg": 12.82, "90-100kg": 13.06, "100-200kg": 11.90, "200-300kg": 11.61,
        "300-500kg": 11.36, "500-700kg": 9.07, "700-1000kg": 8.95, "1000-1500kg": 7.13,
        "1500-2000kg": 6.89, "2000-3000kg": 6.05, ">3000kg": 6.05
    }

    # === Définir les coefficients de zone ===
    st.markdown("### 🎯 Coefficients multiplicateurs par zone")
    coef_zone1 = st.number_input("Coefficient Zone 1", value=1.0, step=0.1)
    coef_zone2 = st.number_input("Coefficient Zone 2", value=1.5, step=0.1)
    coef_zone3 = st.number_input("Coefficient Zone 3", value=2.0, step=0.1)
    coef_dict = {"Zone 1": coef_zone1, "Zone 2": coef_zone2, "Zone 3": coef_zone3}

    df["Tarif de base"] = df["Tranche"].map(tarif_base)
    df["Coef zone"] = df["Zone"].map(coef_dict)
    df["Tarif unitaire"] = (df["Tarif de base"] * df["Coef zone"]).round(2)
    df["Montant"] = (df["Tarif unitaire"]).round(2)

    result = df.groupby(["Zone", "Tranche"]).agg(
        Nb_exp=("Commune", "count"),
        Tarif_unitaire=("Tarif unitaire", "first"),
        Montant_total=("Montant", "sum")
    ).reset_index()

    st.subheader("📋 Grille tarifaire par Zone et Tranche (Forfait × Coefficient)")
    st.dataframe(result)

    fig = px.bar(result, x="Tranche", y="Montant_total", color="Zone",
                 title="Chiffre d'affaires estimé par Zone et Tranche",
                 barmode="group", text_auto=True)
    st.plotly_chart(fig)

    st.download_button("📥 Télécharger la grille tarifaire", result.to_csv(index=False).encode("utf-8"), "grille_tarif_zone_tranche.csv", "text/csv")





st.markdown("---")
st.caption("Normatrans © 2025 - Fennynchaimaa")
