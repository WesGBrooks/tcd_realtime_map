import streamlit as st
import pandas as pd
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Configure page to use full width and hide sidebar
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# # Hide sidebar hamburger menu
# st.markdown(
#     """
#     <style>
#         [data-testid="collapsedControl"] {
#             display: none
#         }
        
#         /* Make the map container full width */
#         .element-container:has(>.stDecoration) {
#             width: 100%;
#             padding: 0;
#             margin: 0;
#         }
        
#         /* Remove default padding */
#         .main > .block-container {
#             padding-top: 0;
#             padding-bottom: 0;
#             padding-left: 0;
#             padding-right: 0;
#         }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

# Initialize the geocoder
geolocator = Nominatim(user_agent="venture_app")

def geocode_address(city, state, country):
    """Geocode an address using city, state, and country"""
    try:
        # Construct address string
        address = f"{city}, {state}, {country}"
        
        # Get location
        location = geolocator.geocode(address)
        
        if location:
            return location.latitude, location.longitude
        return None, None
        
    except (GeocoderTimedOut, GeocoderServiceError):
        # Handle timeout errors
        time.sleep(1)  # Wait a second before returning
        return None, None

# Function to load and process data from public Google Sheet
def load_public_sheet_data():
    try:
        url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRTs5ezNNxS0uBx7Y1jIkJpQHlDfykKPNHPpVlNwAWp5uzS2dKaLg22_p9WpeC0w9Ax7cTPsoGwI3iA/pub?output=csv'
        
        # Read the sheet directly into a dataframe
        df = pd.read_csv(url)
        
        # Create empty columns for coordinates
        if 'latitude' not in df.columns:
            df['latitude'] = None
        if 'longitude' not in df.columns:
            df['longitude'] = None
        
        # Geocode addresses that don't have coordinates
        for idx, row in df.iterrows():
            if pd.isna(row['latitude']) or pd.isna(row['longitude']):
                lat, lon = geocode_address(row['City'], row['State'], row['Country'])
                if lat and lon:
                    df.at[idx, 'latitude'] = lat
                    df.at[idx, 'longitude'] = lon
                    time.sleep(1)  # Be nice to the geocoding service
        
        # Drop rows with missing coordinates
        df = df.dropna(subset=['latitude', 'longitude'])
        
        return df
    except Exception as e:
        st.error(f"Error loading sheet: {str(e)}")
        return None

# Create a placeholder for the map
map_placeholder = st.empty()

# Main loop to refresh the map
while True:
    # Load and display the data
    df = load_public_sheet_data()
    if df is not None:
        with map_placeholder:
            st.map(df)
    
    # Wait for 30 seconds before refreshing
    time.sleep(30)