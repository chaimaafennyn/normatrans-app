import streamlit as st
from datetime import datetime
import pandas as pd
from database import log_action  # tu dois avoir une fonction pour insérer dans la table `logs`

USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "user"},
}

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""

    if st.session_state["authenticated"]:
        return True

    with st.form("login"):
        st.title("🔐 Connexion requise")
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        submit = st.form_submit_button("Se connecter")

        if submit:
            if username == st.secrets["login"]["username"] and password == st.secrets["login"]["password"]:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                log_action(username, "Connexion réussie")  # LOG DANS LA TABLE
                st.success("✅ Connexion réussie")
                st.experimental_rerun()
            else:
                st.error("❌ Identifiants incorrects")
                log_action(username or "Inconnu", "Échec de connexion")
                st.stop()

    st.stop()


def logout():
    if st.sidebar.button("🚪 Se déconnecter"):
        log_action(st.session_state.get("username", "Anonyme"), "Déconnexion")
        st.session_state["authenticated"] = False
        st.experimental_rerun()
