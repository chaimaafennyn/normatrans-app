import streamlit as st
from auth import check_password, logout

st.set_page_config(page_title="Normatrans", layout="wide")

# Sécurité
check_password()
logout()

st.title("🚚 Normatrans - Zones et Tarifs")
st.info("👈 Utilisez le menu à gauche pour naviguer entre les pages.")

