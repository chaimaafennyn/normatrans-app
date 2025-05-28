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

    # === Répartition (en %) des zones par tranche
    repartition = {
        "Tranche de poids": [
            "1 P", "2 P", "3 P", "4 P", "5 P",
            "6 P", "P sup"
        ],
        "Zone 1": [ 47.58, 47.96, 48.94, 51.02, 52.20, 56.41, 84.40 ],
        "Zone 2": [ 35.91, 34.86, 34.54, 33.15, 27.80, 29.91, 11.35 ],
        "Zone 3": [ 16.51, 17.18, 16.52, 15.83, 20.00, 13.68, 4.260 ]
    }
    
    # === Tarifs forfaitaires de base (pondérés)
    tarifs_forfaitaires = {
        "1 P": 34.00, "2 P": 54.00, "3 P": 69.00, "4 P": 83.00,
        "5 P": 97.00, "6 P": 111.00, "P sup": 9.60
    }
    
    # === Paramètres ajustables
    st.markdown("### Paramètres du modèle de calcul")
    a = st.number_input("Écart fixe (en €)", min_value=0.1, max_value=5.0, value=0.29, step=0.01)
    coef_zone2 = st.number_input("Coefficient Zone 2", min_value=0.1, max_value=5.0, value=1.5, step=0.1)
    coef_zone3 = st.number_input("Coefficient Zone 3", min_value=0.1, max_value=5.0, value=3.0, step=0.1)
    
    # === Calcul des tarifs
    df = pd.DataFrame(repartition).set_index("Tranche de poids")
    
    resultats = []
    
    for tranche in df.index:
        r1, r2, r3 = df.loc[tranche, "Zone 1"] / 100, df.loc[tranche, "Zone 2"] / 100, df.loc[tranche, "Zone 3"] / 100
        forfait = tarifs_forfaitaires[tranche]
        x = forfait - a * (coef_zone2 * r2 + coef_zone3 * r3)
        z1 = round(x, 2)
        z2 = round(x + coef_zone2 * a, 2)
        z3 = round(x + coef_zone3 * a, 2)
        total = round(r1 * z1 + r2 * z2 + r3 * z3, 2)
    
        resultats.append({
            "Tranche": tranche,
            "Zone 1 (€)": z1,
            "Zone 2 (€)": z2,
            "Zone 3 (€)": z3,
            "Total pondéré (€)": total
        })
    
    df_resultats = pd.DataFrame(resultats)
    
    # === Affichage
    st.subheader("📊 Résultats du calcul des tarifs")
    st.dataframe(df_resultats)
    
    st.download_button(
        label="📥 Télécharger les résultats",
        data=df_resultats.to_csv(index=False).encode("utf-8"),
        file_name="tarifs_par_tranche.csv",
        mime="text/csv"


else:
    st.warning("⚠️ Veuillez uploader un fichier `pal_tranche.csv` pour démarrer l'analyse.")



