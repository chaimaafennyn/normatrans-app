import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calcul des Tarifs par Zones", layout="wide")

st.title("🚚 Normatrans - Calcul Global des Tarifs par Zones")

# Upload du fichier
uploaded_file = st.file_uploader("Uploader votre fichier de répartition (% d'expéditions par agence et zone)", type=["csv"])

if uploaded_file is not None:
    try:
        # Charger les données
        df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
        st.success("Fichier chargé avec succès !")
        
        # Nettoyer les colonnes
        df = df.rename(columns={"% d'expéditions": "Pourcentage"})
        df["Pourcentage"] = df["Pourcentage"] / 100
        
        # Calcul global
        df_global = df.groupby("Zone")["Pourcentage"].sum().reset_index()
        df_global["Pourcentage"] = df_global["Pourcentage"] / df_global["Pourcentage"].sum()
        
        # Coefficients de pondération
        ponderation = {"Zone 1": 1, "Zone 2": 2, "Zone 3": 3}
        df_global["Pondération"] = df_global["Zone"].map(ponderation)

        # Saisie utilisateur pour le tarif moyen
        tarif_total = st.number_input("Tarif moyen souhaité (€) :", min_value=1.0, max_value=1000.0, value=10.0, step=0.5)

        # Calcul du tarif
        denominateur = (df_global["Pourcentage"] * df_global["Pondération"]).sum()
        base = tarif_total / denominateur
        df_global["Tarif par Zone (€)"] = (df_global["Pondération"] * base).round(2)

        # Affichage des résultats
        st.subheader("Tarifs calculés par Zone :")
        st.dataframe(df_global.style.format({"Pourcentage": "{:.2%}", "Tarif par Zone (€)": "{:.2f}€"}))

        # Téléchargement
        csv = df_global.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Télécharger le fichier des tarifs",
            data=csv,
            file_name='tarifs_par_zone.csv',
            mime='text/csv'
        )

    except Exception as e:
        st.error(f"Erreur lors du traitement : {e}")

else:
    st.info("Veuillez importer un fichier CSV pour démarrer.")

# Footer
st.markdown("---")
st.caption("Normatrans © 2025 - Application développée pour le projet zones & tarifs")
