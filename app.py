import streamlit as st

st.set_page_config(page_title="Normatrans", layout="wide")

from auth import check_password, logout

# Authentification
check_password()
logout()

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

selected_page = st.sidebar.radio("Choisissez une page :", list(pages_admin.keys() if role == "admin" else pages_user.keys()))

# Redirige vers la bonne page via query params (nécessite pages en multi-fichiers dans /pages/)
st.experimental_set_query_params(page=pages_admin[selected_page] if role == "admin" else pages_user[selected_page])

st.success(f"👋 Bienvenue **{username}** — rôle : `{role}`")
