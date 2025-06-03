import streamlit as st
st.set_page_config(page_title="Normatrans - Zones et Tarifs", layout="wide")  # ✅ doit être le tout premier

from auth import check_password, logout  # après la config

# Sécurité
check_password()
logout()


# Message de bienvenue
username = st.session_state.get("username")
role = st.session_state.get("role")

st.success(f"👋 Bonjour **{username}** — Rôle : `{role}`")

if role == "admin":
    st.info("👈 Accès complet (modification, historique...)")
else:
    st.info("👈 Accès limité : consultation uniquement")

