import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.agents import AgentType
from langchain_community.tools.tavily_search import TavilySearchResults

def get_agent(df):
    """
    Creates an agent that has access to:
    1. The Pandas DataFrame (to answer data questions)
    2. The Tavily Search Tool (to answer internet questions)
    """
    
    # 1. Fetch Keys
    # We check Streamlit secrets first (for cloud), then environment variables (for local)
    gemini_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY") or st.secrets.get("TAVILY_API_KEY")

    if not gemini_key or not tavily_key:
        return None

    # 2. Setup LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", # Use a model optimized for function calling
        temperature=0, 
        google_api_key=gemini_key, # Pass the key explicitly
        convert_system_message_to_human=True # Required for best performance with some agent types
    )

    # 3. Setup Internet Search
    search_tool = TavilySearchResults(tavily_api_key=tavily_key, k=1)

    # 4. Create the Agent
    # extra_tools allows the pandas agent to look outside the CSV
    agent = create_pandas_dataframe_agent(
        llm,
        df,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        extra_tools=[search_tool], 
        verbose=True,
        allow_dangerous_code=True,
        handle_parsing_errors=True
    )

    return agent