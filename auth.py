USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "user"},
}

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("🔐 Connexion")
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")

        if st.button("Se connecter"):
            user = USERS.get(username)
            if user and password == user["password"]:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["role"] = user["role"]
                st.rerun()
            else:
                st.error("❌ Identifiants incorrects")

def logout():
    if st.button("🔓 Se déconnecter"):
        st.session_state.clear()
        st.rerun()
