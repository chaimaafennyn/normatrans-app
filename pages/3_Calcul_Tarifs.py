import streamlit as st
import pandas as pd

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🚫 Accès non autorisé. Veuillez vous connecter depuis la page principale.")
    st.stop()
    
st.title("💶 Calcul des Tarifs par Tranche")

# === Répartition (en %) des zones par tranche
repartition = {
    "Tranche de poids": [
        "0-10kg", "10-20kg", "20-30kg", "30-40kg", "40-50kg", "50-60kg", "60-70kg",
        "70-80kg", "80-90kg", "90-100kg", "100-200kg", "200-300kg", "300-500kg",
        "500-700kg", "700-1000kg", "1000-1500kg", "1500-2000kg", "2000-3000kg"
    ],
    "Zone 1": [
        51.54, 50.69, 51.2, 50.46, 49.68, 49.28, 49.22, 49.52, 49.39, 49.64,
        49.92, 49.19, 49.26, 49.91, 48.65, 47.55, 51.67, 42.50
    ],
    "Zone 2": [
        34.25, 36.46, 36.46, 36.97, 37.61, 38.47, 37.62, 37.73, 37.63, 37.05,
        36.7, 36.86, 36.25, 35.24, 36.65, 37.41, 32.59, 36.65
    ],
    "Zone 3": [
        14.21, 12.85, 12.33, 12.57, 12.71, 12.24, 13.16, 12.74, 12.98, 13.31,
        13.39, 13.95, 14.49, 14.85, 14.7, 15.04, 15.74, 20.86
    ]
}

# === Tarifs forfaitaires de base (pondérés)
tarifs_forfaitaires = {
    "0-10kg": 6.50, "10-20kg": 7.00, "20-30kg": 7.40, "30-40kg": 7.80,
    "40-50kg": 8.30, "50-60kg": 8.80, "60-70kg": 9.60, "70-80kg": 9.90,
    "80-90kg": 10.50, "90-100kg": 10.80, "100-200kg": 8.80, "200-300kg": 8.70,
    "300-500kg": 8.60, "500-700kg": 7.25, "700-1000kg": 6.50, "1000-1500kg": 5.20,
    "1500-2000kg": 4.50, "2000-3000kg": 4.00
}

# === Paramètres ajustables
st.markdown("### Paramètres du modèle de calcul")
a = st.number_input("Écart fixe (en €)", min_value=0.1, max_value=5.0, value=0.38, step=0.01)
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
