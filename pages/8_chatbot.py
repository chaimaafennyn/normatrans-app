import streamlit as st
import pandas as pd
import os
from huggingface_hub import InferenceClient
from langchain.llms import HuggingFaceHub
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

st.title("🤖 Chatbot IA sur fichier CSV (via Hugging Face)")

# === Configuration du token (stocké dans secrets.toml) 
HUGGINGFACEHUB_API_TOKEN = st.secrets["HUGGINGFACEHUB_API_TOKEN"]
os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN

# === Upload du fichier CSV
uploaded_file = st.file_uploader("📄 Uploader un fichier CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=";", encoding="latin1")
    st.dataframe(df.head())

    # === Modèle Hugging Face
    llm = HuggingFaceHub(
        repo_id="google/flan-t5-base",
        model_kwargs={"temperature": 0.5, "max_length": 200}
    )

    # === Création de l'agent IA Pandas
    agent = create_pandas_dataframe_agent(llm, df, verbose=True)

    # === Question en langage naturel
    question = st.text_input("💬 Pose ta question (ex : Moyenne des distances par zone)")

    if st.button("🧠 Répondre"):
        try:
            with st.spinner("💬 L'IA réfléchit..."):
                result = agent.run(question)
                st.success("✅ Réponse IA :")
                st.write(result)
        except Exception as e:
            st.error(f"❌ Erreur : {e}")
else:
    st.info("📂 Merci d’uploader un fichier CSV.")

if "HUGGINGFACEHUB_API_TOKEN" not in st.secrets:
    st.error("❌ Clé API Hugging Face manquante dans secrets.")
    st.stop()

