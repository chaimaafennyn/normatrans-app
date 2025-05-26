import streamlit as st

# === Configuration des identifiants ===
CREDENTIALS = {
    "chaimaa": "fennyn2001",
    "normatrans": "normatrans2025"
}

import streamlit as st

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        with st.form("login"):
            st.subheader("🔐 Connexion requise")
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            submitted = st.form_submit_button("Se connecter")
            if submitted:
                if (
                    username == st.secrets["login"]["username"]
                    and password == st.secrets["login"]["password"]
                ):
                    st.session_state["authenticated"] = True
                    st.success("Connexion réussie")
                    st.experimental_rerun()
                else:
                    st.error("Identifiants incorrects")

        st.stop()

def logout():
    if st.sidebar.button("🚪 Se déconnecter"):
        st.session_state["authenticated"] = False
        st.experimental_rerun()
