
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

st.markdown("""
<style>
.big-font {
    font-size:25px !important;
    color: #333;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">Bienvenue sur la plateforme de simulation des tarifs de Normatrans</p>', unsafe_allow_html=True)

# Chargement des données
try:
    df = pd.read_csv("/content/drive/MyDrive/projet_normatrans_zone/nettoyage_de_donnee/repartition_par_agence_et_zone.csv", sep=";", encoding="utf-8")
    df = df.rename(columns={"% d'expéditions": "Pourcentage"})
    df["Pourcentage"] = df["Pourcentage"] / 100
    st.success(" Données chargées avec succès")
except Exception as e:
    st.error(f" Erreur de chargement : {e}")
    st.stop()

# Paramètres utilisateur
tarif_total = st.sidebar.number_input("Entrez le tarif global par agence :", min_value=0.0, value=10.0, step=0.5)

# Coefficients personnalisés par agence
coefs_agence = {
    "NT14G": {"Zone 1": 1, "Zone 2": 1.5, "Zone 3": 2},
    "NT50S": {"Zone 1": 1, "Zone 2": 1.6, "Zone 3": 2.1},
    "NT50V": {"Zone 1": 1, "Zone 2": 1.4, "Zone 3": 1.8},
    "NT50T": {"Zone 1": 1, "Zone 2": 1.7, "Zone 3": 2.2},
    "NT61L": {"Zone 1": 1, "Zone 2": 1.5, "Zone 3": 2},
}

# Calcul des tarifs
def calcul_tarifs(agence_df):
    code = agence_df["Code agence"].iloc[0]
    coef = coefs_agence.get(code, {"Zone 1": 1, "Zone 2": 1.5, "Zone 3": 2})
    agence_df["Coefficient"] = agence_df["Zone"].map(coef)
    denominateur = (agence_df["Pourcentage"] * agence_df["Coefficient"]).sum()
    if denominateur == 0:
        agence_df["Tarif_zone (€)"] = 0
    else:
        base = tarif_total / denominateur
        agence_df["Tarif_zone (€)"] = (agence_df["Coefficient"] * base).round(2)
    return agence_df

df_tarifs = df.groupby("Code agence").apply(calcul_tarifs).reset_index(drop=True)

# Interface utilisateur
st.sidebar.title("Menu")
agences = df_tarifs["Code agence"].unique()
agence_selectionnee = st.sidebar.selectbox(" Choisissez une agence :", agences)

# Filtrage
df_agence = df_tarifs[df_tarifs["Code agence"] == agence_selectionnee]

# Statistiques
st.subheader(" Détail des tarifs par zone")
col1, col2, col3 = st.columns(3)
col1.metric("Tarif Zone 1 (€)", df_agence[df_agence["Zone"] == "Zone 1"]["Tarif_zone (€)"].values[0])
col2.metric("Tarif Zone 2 (€)", df_agence[df_agence["Zone"] == "Zone 2"]["Tarif_zone (€)"].values[0])
col3.metric("Tarif Zone 3 (€)", df_agence[df_agence["Zone"] == "Zone 3"]["Tarif_zone (€)"].values[0])

# Graphique Plotly
fig = px.pie(df_agence, names="Zone", values="Pourcentage", title="Répartition des expéditions par zone (%)")
st.plotly_chart(fig)

# Tableau récapitulatif
st.write("### Tableau récapitulatif")
st.dataframe(df_agence[["Zone", "Pourcentage", "Coefficient", "Tarif_zone (€)"]])

# Export CSV
st.download_button(
    label="Télécharger les tarifs de cette agence",
    data=df_agence.to_csv(index=False),
    file_name=f"{agence_selectionnee}_tarifs.csv",
    mime="text/csv"
)

# Crédit bas de page
st.markdown("---")
st.caption("Normatrans © 2025")
