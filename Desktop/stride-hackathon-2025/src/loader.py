import pandas as pd
import streamlit as st
import os
from datetime import datetime

@st.cache_data
def load_dataset(file_name="emissions.csv"):
    """
    Loads, cleans, and transforms the raw OWID CO2 data.
    Works both locally and on Streamlit Cloud.
    """

    # base_dir = .../Desktop/stride-hackathon-2025
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "data", file_name)

    if not os.path.exists(file_path):
        st.error(f"Error: The file was not found at: {file_path}")
        st.stop()  # stop the app instead of returning an empty df

    df_raw = pd.read_csv(file_path)

    # Define the columns that represent different sectors/fuels
    sector_columns = [
        "coal_co2", "oil_co2", "gas_co2", "cement_co2",
        "flaring_co2", "other_industry_co2", "land_use_change_co2",
    ]
    
    df_selected = df_raw[["country", "year"] + sector_columns]
    df_selected = df_selected.rename(columns={"country": "Entity", "year": "Year"})
    
    # --- MELT: Transform Wide to Long Format ---
    df_long = df_selected.melt(
        id_vars=["Entity", "Year"],
        value_vars=sector_columns,
        var_name="Sector",
        value_name="Emissions",
    )
    
    # Clean up and title-case sector names
    df_long["Sector"] = df_long["Sector"].str.replace("_co2", "", regex=False).str.title()
    
    # Final Cleaning and Filtering
    df_final = df_long.dropna(subset=["Emissions"])
    df_final["Year"] = df_final["Year"].astype(int)
    
    # Filter out non-country aggregates (like 'World', 'Europe', etc.)
    df_final = df_final[df_final["Entity"].apply(lambda x: not x.isupper())]
    
    # --- PERFORMANCE OPTIMIZATION ---
    current_year = datetime.now().year
    df_final = df_final[df_final["Year"] >= (current_year - 25)]

    return df_final[["Entity", "Year", "Sector", "Emissions"]]
