import streamlit as st
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm.local_llm import LocalLLM

st.title("💬 Chatbot IA avec PandasAI (Gratuit & Local)")

# Chargement du fichier CSV
uploaded_file = st.file_uploader("📄 Uploader un fichier CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=";")
    st.write("📊 Données chargées :", df.head())

    # Setup du modèle local via Ollama
    llm = LocalLLM(api_base="http://localhost:11434", model="llama3")
    sdf = SmartDataframe(df, config={"llm": llm})

    question = st.text_input("💬 Pose ta question (ex : Moyenne des distances par zone)")

    if st.button("🧠 Répondre"):
        if question:
            with st.spinner("Réflexion en cours..."):
                try:
                    answer = sdf.chat(question)
                    st.success("🧠 Réponse IA :")
                    st.write(answer)
                except Exception as e:
                    st.error(f"Erreur : {e}")
        else:
            st.warning("❗ Pose une question avant de cliquer.")
