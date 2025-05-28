c'est bon comment ajouter ces coef dans ce calcul import streamlit as st
import pandas as pd

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🚫 Accès non autorisé. Veuillez vous connecter depuis la page principale.")
    st.stop()
    
st.title("💶 Calcul des Tarifs par Tranche")

# === Répartition (en %) des zones par tranche
repartition = {
    "Tranche de poids": [
        "1 P", "2 P", "3 P", "4 P", "5 P", "6 P", "P sup"],
    "Zone 1": [ 47.58, 47.96, 48.94, 51.02, 52.20, 56.41, 84.40 ],
    "Zone 2": [ 35.91, 34.86, 34.54, 33.15, 27.80, 29.91, 11.35 ],
    "Zone 3": [ 16.51, 17.18, 16.52, 15.83, 20.00, 13.68, 04.26 ]
}

# === Tarifs forfaitaires de base (pondérés)
tarifs_forfaitaires = {
    "1 P": 34.00, "2 P": 54.00, "3 P": 69.00, "4 P": 83.00,
    "5 P": 97.00, "6 P": 111.00, "P sup": 9.60
}

# === Paramètres ajustables
st.markdown("### Paramètres du modèle de calcul")
a = st.number_input("Écart fixe (en €)", min_value=0.1, max_value=5.0, value=1.44, step=0.01)
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
) 
