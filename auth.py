import streamlit as st
from datetime import datetime
from database import log_action

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("🔐 Connexion requise")

        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")

        if st.button("Se connecter"):
            valid_username = st.secrets["login"]["username"]
            valid_password = st.secrets["login"]["password"]

            if username == valid_username and password == valid_password:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.success("✅ Connexion réussie")
                log_action(username, "Connexion réussie")
            else:
                st.error("❌ Identifiants incorrects")
                log_action(username, "Échec de connexion")

        st.stop()

def logout():
    if st.sidebar.button("🚪 Se déconnecter"):
        log_action(st.session_state.get("username", "inconnu"), "Déconnexion")
        st.session_state.clear()
        st.experimental_rerun()
