import streamlit as st
import hashlib

import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

def check_password():
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    # 🔒 Liste des utilisateurs autorisés (à adapter)
    users = {
        "chaimaa": hash_password("fennyn27072001"),
        "normatrans": hash_password("normatrans2025")
    }

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""

    if not st.session_state["authenticated"]:
        st.title("🔐 Connexion requise")
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")

        if st.button("Se connecter"):
            if username in users and hash_password(password) == users[username]:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.success("✅ Connexion réussie")
                st.rerun()
            else:
                st.error("❌ Identifiants incorrects")
        st.stop()

def logout():
    if st.sidebar.button("🔒 Se déconnecter"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.rerun()

check_password()
logout()
 
st.set_page_config(page_title="Normatrans - Zones et Tarifs", layout="wide")

st.title("🚚 Normatrans - Zones et Tarifs de Livraison")

menu = st.sidebar.radio(
    "Navigation",
    ["Analyse des Zones",  "Analyse des Tranches de Poids", "Calcul des Tarifs par Tranche"],
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
# Partie 2 : Analyse des Tranches de Poids
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

    # Ajouter une ligne globale (toutes zones confondues)
    total_global = df_filtered.groupby("Tranche").size()
    total_global_percent = (total_global / total_global.sum() * 100).round(2)
    tableau.loc["Total"] = total_global_percent
    st.dataframe(tableau)

    # === Zones par tranches ===
    st.subheader("📊 Répartition (%) des zones par tranche de poids")
    pivot_inverse = df_filtered.groupby(["Tranche", "Zone"]).size().reset_index(name="Nb_exp")
    totaux_tranche = pivot_inverse.groupby("Tranche")["Nb_exp"].sum().reset_index(name="Total")
    result_inv = pd.merge(pivot_inverse, totaux_tranche, on="Tranche")
    result_inv["Pourcentage"] = (result_inv["Nb_exp"] / result_inv["Total"] * 100).round(2)
    tableau_inverse = result_inv.pivot(index="Tranche", columns="Zone", values="Pourcentage").fillna(0)
    # Transposer pour afficher les tranches en colonnes et zones en lignes
    tableau_inverse = tableau_inverse.T
    st.dataframe(tableau_inverse)

 
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

    # === Top 20 communes
    if "Commune" in detail.columns:
        st.subheader("🏆 Top 20 communes avec le plus d'expéditions")
        top_communes = detail.groupby("Commune")["Nb_expéditions"].sum().nlargest(20).reset_index()
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
# Partie 3 : Calcul des Tarifs par Tranche (Méthode Écart Fixe)
# =======================
elif menu == "Calcul des Tarifs par Tranche":
    st.header("💶 Calcul des Tarifs par Tranche")

    # Répartition (pourcentage) par tranche
    repartition = {
        "Tranche de poids": [
            "0-10kg", "10-20kg", "20-30kg", "30-40kg", "40-50kg", "50-60kg", "60-70kg",
            "70-80kg", "80-90kg", "90-100kg", "100-200kg", "200-300kg", "300-500kg",
            "500-700kg", "700-1000kg", "1000-1500kg", "1500-2000kg", "2000-3000kg", ">3000kg"
        ],
        "Zone 1": [
            51.54, 50.69, 51.2, 50.46, 49.68, 49.28, 49.22, 49.52, 49.39, 49.64,
            49.92, 49.19, 49.26, 49.26, 49.91, 48.65, 47.55, 51.67, 44.64
        ],
        "Zone 2": [
            34.25, 36.46, 36.46, 36.97, 37.61, 38.47, 37.62, 37.73, 37.63, 37.05,
            36.7, 36.86, 36.25, 35.24, 36.65, 37.41, 32.59, 36.65, 36.9
        ],
        "Zone 3": [
            14.21, 12.85, 12.33, 12.57, 12.71, 12.24, 13.16, 12.74, 12.98, 13.31,
            13.39, 13.95, 14.49, 14.85, 14.7, 15.04, 15.74, 20.86, 18.45
        ]
    }

    tarifs_forfaitaires = {
        "0-10kg": 8.58, "10-20kg": 8.95, "20-30kg": 9.43, "30-40kg": 9.79,
        "40-50kg": 10.52, "50-60kg": 10.88, "60-70kg": 11.73, "70-80kg": 12.09,
        "80-90kg": 12.82, "90-100kg": 13.06, "100-200kg": 11.90, "200-300kg": 11.61,
        "300-500kg": 11.36, "500-700kg": 9.07, "700-1000kg": 8.95, "1000-1500kg": 7.13,
        "1500-2000kg": 6.89, "2000-3000kg": 6.05, ">3000kg": 6.36
    }

    # Entrées utilisateurs
    st.markdown("### Paramètres ajustables")
    a = st.number_input("Écart fixe (en €)", min_value=0.1, max_value=5.0, value=0.38, step=0.01)
    coef_zone2 = st.number_input("Coefficient Zone 2", min_value=0.1, max_value=5.0, value=1.5, step=0.1)
    coef_zone3 = st.number_input("Coefficient Zone 3", min_value=0.1, max_value=5.0, value=3.0, step=0.1)

    df = pd.DataFrame(repartition).set_index("Tranche de poids")

    res_m1 = []
    for tranche in df.index:
        r1, r2, r3 = df.loc[tranche, "Zone 1"] / 100, df.loc[tranche, "Zone 2"] / 100, df.loc[tranche, "Zone 3"] / 100
        forfait = tarifs_forfaitaires[tranche]
        x = forfait - a * (coef_zone2 * r2 + coef_zone3 * r3)
        z1 = round(x, 2)
        z2 = round(x + coef_zone2 * a, 2)
        z3 = round(x + coef_zone3 * a, 2)
        total = round(r1 * z1 + r2 * z2 + r3 * z3, 2)

        res_m1.append({
            "Tranche": tranche,
            "Zone 1 (€)": z1,
            "Zone 2 (€)": z2,
            "Zone 3 (€)": z3,
            "Total pondéré (€)": total
        })

    df_resultats1 = pd.DataFrame(res_m1)
    st.subheader("📋 Résultat du calcul des tarifs")
    st.dataframe(df_resultats1)

    st.download_button(
        "📥 Télécharger les tarifs par tranche",
        data=df_resultats1.to_csv(index=False).encode("utf-8"),
        file_name="tarifs_par_tranche_methode_ecart_fixe.csv",
        mime="text/csv"
    )





st.markdown("---")
st.caption("Normatrans © 2025 - Fennynchaimaa")
