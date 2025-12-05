import streamlit as st
import plotly.express as px
from dotenv import load_dotenv

# Import our custom modules
from src.loader import load_dataset
from src.agent import get_agent

# Load local environment variables
load_dotenv()

# Page Config
st.set_page_config(page_title="Stride Emissions Intel", layout="wide")

def main():
    st.title("🌍 Stride Labs: Emissions Intel Dashboard")
    st.markdown("### HackForward 2025 Round 2 Submission")

    # ---------------------------
    # 1. LOAD DATA
    # ---------------------------
    df = load_dataset(file_path="emissions.csv")
    
    if df is None:
        st.error("Data not found! Please check 'data/emissions.csv'.")
        st.stop()

    # ---------------------------
    # 2. SIDEBAR FILTERS
    # ---------------------------
    st.sidebar.header("Filter Data")
    
    # Country Filter
    countries = sorted(df['Entity'].unique())
    selected_countries = st.sidebar.multiselect("Select Countries", countries, default=countries[:2])
    
    # Sector Filter
    sectors = sorted(df['Sector'].unique())
    selected_sectors = st.sidebar.multiselect("Select Sectors", sectors, default=sectors[:2])

    # Apply Filters
    if selected_countries and selected_sectors:
        filtered_df = df[
            (df['Entity'].isin(selected_countries)) & 
            (df['Sector'].isin(selected_sectors))
        ]
    else:
        filtered_df = df

    # ---------------------------
    # 3. DASHBOARD VISUALS
    # ---------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Emission Trends")
        if not filtered_df.empty:
            # Aggregate data to avoid messy lines if multiple entries exist per year
            line_data = filtered_df.groupby(['Year', 'Entity'])['Emissions'].sum().reset_index()
            fig = px.line(line_data, x='Year', y='Emissions', color='Entity', markers=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data for current selection.")

    with col2:
        st.subheader("🏭 Sector Breakdown")
        if not filtered_df.empty:
            # Bar chart
            fig_bar = px.bar(filtered_df, x='Sector', y='Emissions', color='Entity', barmode='group')
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No data for current selection.")

    st.divider()

    # ---------------------------
    # 4. CHAT INTERFACE
    # ---------------------------
    st.subheader("🤖 Data Agent (Internet Enabled)")
    
    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! Ask me about the data above, or ask me to search the web for climate policies."}
        ]

    # Display History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Initialize Agent
    agent = get_agent(df) # Pass the FULL df to the agent, not just filtered
    
    if agent is None:
        st.error("⚠️ API Keys missing! Please set OPENAI_API_KEY and TAVILY_API_KEY.")

    # User Input
    if prompt := st.chat_input("E.g. 'Compare US and India emissions in 2023 and find reasons why.'"):
        
        # 1. Display User Message
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 2. Generate Response
        with st.chat_message("assistant"):
            if agent:
                with st.spinner("Analyzing data & searching web..."):
                    try:
                        response = agent.run(prompt)
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.error("Agent could not be initialized. Check API keys.")

if __name__ == "__main__":
    main()