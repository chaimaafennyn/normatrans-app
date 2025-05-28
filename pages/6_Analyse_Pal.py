import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📦 Analyse des Tranches de Palette (UM) par Zone")

uploaded_file = st.file_uploader("📄 Uploader le fichier des livraisons (pal_tranche.csv)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=";", encoding="latin1")

    # Nettoyage
    df.columns = df.columns.str.strip()
    df["UM"] = df["UM"].astype(str).str.replace(",", ".").astype(float)
    df["Zone"] = df["Zone"].astype(str).str.strip()
    if "Code agence" in df.columns:
        df["Code agence"] = df["Code agence"].astype(str).str.strip()

    # Tranches UM
    bins = [0, 1, 2, 3, 4, 5, 6, float("inf")]
    labels = ["1 palette", "2 palettes", "3 palettes", "4 palettes", "5 palettes", "6 palettes", "+6 palettes"]
    df["Tranche_UM"] = pd.cut(df["UM"], bins=bins, labels=labels, right=True)
    df["Tranche_UM"] = pd.Categorical(df["Tranche_UM"], categories=labels, ordered=True)
    df = df[df["Tranche_UM"].notna()]

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

    # === Répartition par zone
    st.subheader("📊 Répartition (%) des tranches de palette par zone")
    pivot = df_filtered.groupby(["Zone", "Tranche_UM"]).size().reset_index(name="Nb_exp")
    totaux = pivot.groupby("Zone")["Nb_exp"].sum().reset_index(name="Total")
    result = pd.merge(pivot, totaux, on="Zone")
    result["Pourcentage"] = (result["Nb_exp"] / result["Total"] * 100).round(2)
    tableau = result.pivot(index="Zone", columns="Tranche_UM", values="Pourcentage").fillna(0)
    tableau = tableau[tableau.index.notna()]  # ✅ corriger ligne NaN
    st.dataframe(tableau)

    st.download_button(
        "📥 Télécharger la répartition par zone",
        data=tableau.to_csv().encode("utf-8"),
        file_name="repartition_tranches_palette_par_zone.csv",
        mime="text/csv"
    )

    # === Répartition des zones par tranche
    st.subheader("🔁 Répartition (%) des zones par tranche de palette (UM)")
    pivot_inv = df_filtered.groupby(["Tranche_UM", "Zone"]).size().reset_index(name="Nb_exp")
    totaux_tranche = pivot_inv.groupby("Tranche_UM")["Nb_exp"].sum().reset_index(name="Total")
    result_inv = pd.merge(pivot_inv, totaux_tranche, on="Tranche_UM")
    result_inv["Pourcentage"] = (result_inv["Nb_exp"] / result_inv["Total"] * 100).round(2)
    tableau_inverse = result_inv.pivot(index="Tranche_UM", columns="Zone", values="Pourcentage").fillna(0)
    tableau_inverse = tableau_inverse[tableau_inverse.index.notna()]  # ✅ corriger ligne NaN
    st.dataframe(tableau_inverse)

    # === Détail global
    st.subheader("📋 Détail global par agence, zone et commune")
    group_cols = ["Zone", "Commune"]
    if "Code agence" in df_filtered.columns:
        group_cols.insert(0, "Code agence")

    detail = df_filtered.groupby(group_cols).agg(
        Nb_expéditions=("UM", "count"),
        UM_total=("UM", "sum"),
        UM_moyenne=("UM", "mean")
    ).reset_index().round(2)

    if st.checkbox("📄 Afficher le détail des données"):
        st.dataframe(detail)

    # === Top communes
    if "Commune" in detail.columns:
        st.subheader("🏆 Top 20 communes avec le plus d'expéditions")
        top_communes = detail.groupby("Commune")["Nb_expéditions"].sum().nlargest(20).reset_index()
        st.bar_chart(top_communes.set_index("Commune")["Nb_expéditions"])

    # === Statistiques globales
    st.subheader("⚖️ Statistiques globales")
    stats_zone = df_filtered.groupby("Zone").agg(
        Nb_expéditions=("UM", "count"),
        UM_total=("UM", "sum"),
        UM_moyenne=("UM", "mean")
    ).round(2)
    st.dataframe(stats_zone)

    if "Code agence" in df_filtered.columns:
        st.subheader("🏢 Statistiques par Agence")
        stats_agence = df_filtered.groupby("Code agence").agg(
            Nb_expéditions=("UM", "count"),
            UM_total=("UM", "sum"),
            UM_moyenne=("UM", "mean")
        ).round(2)
        st.dataframe(stats_agence)

    # === Graphiques camembert
    st.subheader("🥧 Répartition globale des tranches de palette")
    pie_tranches = df_filtered["Tranche_UM"].value_counts().sort_index().reset_index()
    pie_tranches.columns = ["Tranche_UM", "Nb_exp"]
    fig = px.pie(pie_tranches, names="Tranche_UM", values="Nb_exp", title="Répartition des tranches UM")
    st.plotly_chart(fig)

    pie_zones = df_filtered["Zone"].value_counts().reset_index()
    pie_zones.columns = ["Zone", "Nb_exp"]
    fig = px.pie(pie_zones, names="Zone", values="Nb_exp", title="Répartition par zone")
    st.plotly_chart(fig)

    if "Code agence" in df_filtered.columns:
        pie_agence = df_filtered["Code agence"].value_counts().reset_index()
        pie_agence.columns = ["Code agence", "Nb_exp"]
        fig = px.pie(pie_agence, names="Code agence", values="Nb_exp", title="Répartition par agence")
        st.plotly_chart(fig)

else:
    st.warning("⚠️ Veuillez uploader un fichier `pal_tranche.csv` pour démarrer l'analyse.")



