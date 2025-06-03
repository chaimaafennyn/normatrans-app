import streamlit as st
import pandas as pd
import os
from pandasai import SmartDataframe
from pandasai.llm import HuggingFaceLLM


# Titre de la page
st.title("🤖 Chatbot IA sur votre fichier CSV (gratuit via Hugging Face)")

# === Clé HuggingFace depuis secrets ===
HUGGINGFACEHUB_API_TOKEN = st.secrets["HUGGINGFACEHUB_API_TOKEN"]

# === Chargement du fichier CSV ===
uploaded_file = st.file_uploader("📄 Upload ton fichier CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=";", encoding="latin1")
    st.dataframe(df.head())

    # === Initialiser LLM Hugging Face ===
    llm = HuggingFaceLLM(api_token=HUGGINGFACEHUB_API_TOKEN, model="google/flan-t5-base")
    sdf = SmartDataframe(df, config={"llm": llm})

    # === Interface de question ===
    question = st.text_input("💬 Pose ta question (ex : Moyenne des distances par zone)")

    if st.button("🧠 Répondre"):
        with st.spinner("Réflexion en cours..."):
            try:
                response = sdf.chat(question)
                st.success("✅ Réponse :")
                st.write(response)
            except Exception as e:
                st.error(f"❌ Erreur : {e}")
else:
    st.info("📂 Veuillez d'abord uploader un fichier CSV.")
