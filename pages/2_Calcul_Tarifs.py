import streamlit as st
import pandas as pd

st.header("💶 Calcul Global des Tarifs Pondérés par Zones")

default_tarif_file = "repartition_par_zone.csv"
uploaded_tarif = st.file_uploader("Uploader un autre fichier de répartition (optionnel)", type=["csv"])

if uploaded_tarif is not None:
    df_tarif = pd.read_csv(uploaded_tarif, sep=";", encoding="utf-8")
    st.success("✅ Nouveau fichier de répartition chargé !")
else:
    df_tarif = pd.read_csv(default_tarif_file, sep=";", encoding="utf-8")
    st.info(f"📂 Fichier par défaut chargé : {default_tarif_file}")

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

    st.download_button(
        label="📥 Télécharger le fichier des tarifs",
        data=df_global.to_csv(index=False).encode('utf-8'),
        file_name='tarifs_par_zone.csv',
        mime='text/csv'
    )

except Exception as e:
    st.error(f"❌ Erreur : {e}")
