import streamlit as st
import hashlib
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
from database import get_tranches

st.title("📦 Analyse des Tranches de Poids par Zone")

uploaded_file = st.file_uploader("📄 Uploader un fichier CSV (optionnel)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=";", encoding="latin1")
    st.success("✅ Fichier CSV chargé")
else:
    df = get_tranches()
    st.success("✅ Données chargées depuis Supabase")


    # Nettoyage
    df["Poids"] = df["Poids"].astype(str).str.replace(",", ".").astype(float)
    df["Zone"] = df["Zone"].astype(str).str.strip()
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
    tableau_inverse = result_inv.pivot(index="Tranche", columns="Zone", values="Pourcentage").fillna(0).T
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

    # === Statistiques globales
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

    # === Graphiques
    st.subheader("🥧 Graphiques de répartition globaux")

    pie_tranches = df_filtered["Tranche"].value_counts().reset_index()
    pie_tranches.columns = ["Tranche", "Nb_exp"]
    fig = px.pie(pie_tranches, names="Tranche", values="Nb_exp", title="Répartition des tranches de poids")
    st.plotly_chart(fig)

    zone_exp = df_filtered["Zone"].value_counts().reset_index()
    zone_exp.columns = ["Zone", "Nb_exp"]
    fig = px.pie(zone_exp, names="Zone", values="Nb_exp", title="Expéditions par Zone")
    st.plotly_chart(fig)

    if "Code agence" in df_filtered.columns:
        agence_exp = df_filtered["Code agence"].value_counts().reset_index()
        agence_exp.columns = ["Code agence", "Nb_exp"]
        fig = px.pie(agence_exp, names="Code agence", values="Nb_exp", title="Expéditions par Agence")
        st.plotly_chart(fig)

    zone_poids = df_filtered.groupby("Zone")["Poids"].sum().reset_index()
    fig = px.pie(zone_poids, names="Zone", values="Poids", title="Poids total (kg) par Zone")
    st.plotly_chart(fig)

    if "Code agence" in df_filtered.columns:
        poids_agence = df_filtered.groupby("Code agence")["Poids"].sum().reset_index()
        fig = px.pie(poids_agence, names="Code agence", values="Poids", title="Poids total (kg) par Agence")
        st.plotly_chart(fig)

    if "UM" in df_filtered.columns:
        zone_um = df_filtered.groupby("Zone")["UM"].sum().reset_index()
        fig = px.pie(zone_um, names="Zone", values="UM", title="UM total par Zone")
        st.plotly_chart(fig)

        if "Code agence" in df_filtered.columns:
            um_agence = df_filtered.groupby("Code agence")["UM"].sum().reset_index()
            fig = px.pie(um_agence, names="Code agence", values="UM", title="UM total par Agence")
            st.plotly_chart(fig)
