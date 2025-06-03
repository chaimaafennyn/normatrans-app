import streamlit as st
from pandasai import SmartDataframe
from pandasai.llm.openai import OpenAI
import pandas as pd
import os

# === Authentification requise
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🚫 Accès non autorisé. Veuillez vous connecter depuis la page principale.")
    st.stop()

st.title("🤖 Chatbot IA - Questions sur les données")

# === Clé API OpenAI
openai_api_key = st.secrets["openai"]["api_key"]  # Tu dois la stocker dans .streamlit/secrets.toml

# === Charger le fichier CSV
uploaded_file = st.file_uploader("📄 Uploader un fichier CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=";", encoding="latin1")
    st.success("✅ Fichier chargé")

    st.dataframe(df.head(5))

    # Préparer l'IA
    llm = OpenAI(api_token=openai_api_key, model="gpt-3.5-turbo", temperature=0)
    sdf = SmartDataframe(df, config={"llm": llm})

    # Entrée utilisateur
    question = st.text_input("💬 Pose ta question (ex : Moyenne des distances par zone)")

    if question:
        with st.spinner("🤔 L'IA réfléchit..."):
            try:
                response = sdf.chat(question)
                st.markdown(f"🧠 **Réponse IA :**\n\n{response}")
            except Exception as e:
                st.error(f"❌ Erreur : {e}")

else:
    st.info("📂 Merci d'uploader un fichier pour interroger l'IA.")
