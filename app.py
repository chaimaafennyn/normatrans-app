import streamlit as st
st.set_page_config(page_title="Normatrans - Zones et Tarifs", layout="wide")  # ✅ doit être le tout premier

from auth import check_password, logout  # après la config

# Sécurité
check_password()
logout()

st.title("🚚 Normatrans - Zones et Tarifs")
st.info("👈 Utilisez le menu à gauche pour naviguer entre les pages.")


