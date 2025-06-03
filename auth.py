import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
from database import log_action  # 🆕 Pour journaliser

# === Identifiants avec rôles ===
CREDENTIALS = {
    "admin": {"password": "azerty123", "role": "admin"},
    "client": {"password": "fennyn", "role": "client"}
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
            user_data = CREDENTIALS.get(username)
            if user_data and user_data["password"] == password:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["role"] = user_data["role"]

                # ✅ Log de connexion
                log_action(username, "Connexion", "Connexion réussie à l'application")

                st.success("✅ Connexion réussie.")
                st.rerun()
            else:
                st.error("❌ Identifiants incorrects.")
        st.stop()

def logout():
    if st.sidebar.button("🔒 Se déconnecter"):
        username = st.session_state.get("username", "inconnu")

        # ✅ Log de déconnexion
        log_action(username, "Déconnexion", "Utilisateur déconnecté de l'application")

        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.session_state["role"] = ""
        st.rerun()
