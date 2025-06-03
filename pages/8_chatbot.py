import streamlit as st
import pandas as pd
from langchain.llms import HuggingFaceHub
from langchain.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
import os

st.title("🤖 Chatbot IA sur votre fichier CSV (gratuit via HuggingFace)")

# Clé Hugging Face gratuite (tu dois créer un compte sur huggingface.co)
HUGGINGFACEHUB_API_TOKEN = st.secrets["HUGGINGFACEHUB_API_TOKEN"]
os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN

uploaded_file = st.file_uploader("📄 Upload ton CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=";", encoding="latin1")
    st.dataframe(df.head())

    # Utiliser un LLM gratuit de HuggingFace
    llm = HuggingFaceHub(repo_id="google/flan-t5-base", model_kwargs={"temperature": 0.5, "max_length": 200})

    # Créer l'agent IA
    agent = create_pandas_dataframe_agent(llm, df, verbose=False, agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION)

    question = st.text_input("💬 Pose ta question en langage naturel (ex: Moyenne des distances par zone)")

    if st.button("🧠 Répondre"):
        try:
            with st.spinner("Réflexion en cours..."):
                response = agent.run(question)
                st.success("✅ Réponse :")
                st.write(response)
        except Exception as e:
            st.error(f"Erreur : {e}")
