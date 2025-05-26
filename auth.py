import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

# ✅ Cette ligne DOIT venir immédiatement après les imports
st.set_page_config(page_title="Normatrans - Zones et Tarifs", layout="wide")

# === Authentification (à mettre après set_page_config) ===
CREDENTIALS = {
    "admin": "azerty123",
    "client": "test2025"
}

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("🔐 Connexion requise")
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        login = st.button("Se connecter")

        if login:
            if username in CREDENTIALS and CREDENTIALS[username] == password:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.success("✅ Connexion réussie.")
                st.rerun()
            else:
                st.error("❌ Identifiants incorrects.")
        st.stop()

def logout():
    if st.sidebar.button("🔒 Se déconnecter"):
        st.session_state["authenticated"] = False
        st.rerun()

check_password()
logout()

# Le reste de ton code Streamlit vient après…
