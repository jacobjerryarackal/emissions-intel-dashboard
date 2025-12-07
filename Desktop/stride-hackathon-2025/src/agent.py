import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_experimental.agents import create_pandas_dataframe_agent


def get_agent(df):
    """
    Creates an agent that can analyze the provided Pandas DataFrame.

    Uses Groq's Llama 3.1 models (fast + generous free tier)
    and does NOT use internet search tools, only your emissions dataset.
    """

    # 1. Fetch Groq API key
    groq_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
    if not groq_key:
        st.error("⚠️ GROQ_API_KEY is missing. Please set it in Streamlit secrets or your .env file.")
        return None

    # 2. Setup LLM from Groq
    llm = ChatGroq(
        groq_api_key=groq_key,
        model_name="llama-3.1-8b-instant",  # good balance of speed & quality
        temperature=0,
        max_retries=1,
        max_tokens=512,
    )

    # 3. Create Pandas DataFrame Agent
    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=False,
        allow_dangerous_code=True,          # required for pandas execution
        handle_parsing_errors=True,
    )

    return agent
