import streamlit as st

def login():
    st.title("🔐 Connexion")

    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        if username == st.secrets["login"]["username"] and password == st.secrets["login"]["password"]:
            st.session_state["auth"] = True
            st.success("Connexion réussie !")
        else:
            st.error("Identifiants incorrects")

    return st.session_state.get("auth", False)
