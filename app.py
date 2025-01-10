import streamlit as st
import pandas as pd
import time

# Configure page to use full width
st.set_page_config(layout="wide")

# Function to load data from public Google Sheet
def load_public_sheet_data(sheet_url):
    try:
        # Convert the sheet URL to the export URL
        sheet_id = sheet_url.split('/')[5]  # Extract the sheet ID from the URL
        url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'
        
        # Read the sheet directly into a dataframe
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Error loading sheet: {str(e)}")
        return None

# URL of your public Google Sheet
SHEET_URL = "YOUR_GOOGLE_SHEET_URL"  # Replace with your public sheet URL

# Create a placeholder for the map
map_placeholder = st.empty()

# Infinite loop to refresh the map
while True:
    # Load and display the data
    df = load_public_sheet_data(SHEET_URL)
    if df is not None:
        with map_placeholder:
            st.map(df)
    
    # Wait for 3 seconds
    time.sleep(3)