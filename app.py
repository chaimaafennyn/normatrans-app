import streamlit as st
from auth import check_password, logout

# Authentification
check_password()
logout()

st.set_page_config(page_title="Normatrans", layout="wide")
username = st.session_state.get("username", "")
role = "admin" if username == "admin" else "utilisateur"

# === MENU LATÉRAL DYNAMIQUE
st.sidebar.title("📂 Navigation")
pages_admin = {
    "🏠 Accueil": "Accueil",
    "📦 Analyse Zones": "1_Analyse_Zones",
    "📊 Analyse Tranches Poids": "2_Analyse_Tranches_Poids",
    "📦 Analyse Tranches Palette": "3_Analyse_Tranches_Palette",
    "🕵️ Historique": "99_Historique"
}
pages_user = {
    "🏠 Accueil": "Accueil",
    "📦 Analyse Zones": "1_Analyse_Zones",
    "📊 Analyse Tranches Poids": "2_Analyse_Tranches_Poids",
    "📦 Analyse Tranches Palette": "3_Analyse_Tranches_Palette"
}
