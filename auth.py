import streamlit as st

# === Configuration des identifiants ===
CREDENTIALS = {
    "chaimaa": "fennyn2001",
    "normatrans": "normatrans2025"
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

# === Déconnexion
def logout():
    if st.sidebar.button("🔒 Se déconnecter"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.rerun()
