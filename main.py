import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Charger config
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Authentification
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, auth_status, username = authenticator.login("Login", "main")

if auth_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Bienvenue {name} !")
    st.title("Bienvenue sur Normatrans App")
    st.write("Choisissez une page dans le menu.")
elif auth_status is False:
    st.error("Identifiants incorrects")
elif auth_status is None:
    st.warning("Veuillez entrer vos identifiants")
