import streamlit as st
import pandas as pd
import time
from geopy.geocoders import ArcGIS
from geopy.extra.rate_limiter import RateLimiter
import random
import json
import os

# Configure page to use full width and hide sidebar
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Initialize session state for geocoding cache if it doesn't exist
if 'geocode_cache' not in st.session_state:
    st.session_state.geocode_cache = {}

# Initialize the geocoder with increased timeout
geolocator = ArcGIS(user_agent="tcd_realtime_map", timeout=10)

# Create a rate-limited version of the geocoding function
geocode = RateLimiter(geolocator.geocode, 
                      min_delay_seconds=0.5,
                      max_retries=3,
                      error_wait_seconds=2.0)

def generate_random_color():
    """Generate a random color in hex format with 75% opacity"""
    return '#{:06x}BF'.format(random.randint(0, 0xFFFFFF))

def geocode_address(city, state, country):
    """Geocode an address using city, state, and country with caching"""
    try:
        # Construct address string
        address = f"{city}, {state}, {country}"
        
        # Check cache first
        if address in st.session_state.geocode_cache:
            return st.session_state.geocode_cache[address]
        
        # Get location with rate limiting and retries
        location = geocode(address)
        
        if location:
            # Store in cache
            coords = (location.latitude, location.longitude)
            st.session_state.geocode_cache[address] = coords
            return coords
            
        return None, None
        
    except Exception as e:
        print(f"Geocoding error for {address}: {str(e)}")
        return None, None

def load_public_sheet_data():
    try:
        url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSze68vYCM-BtlfuWVgzY6Wayf3Ry0k3o0mR7yDM5lYbvtSU_k3hu4V0uPiy0Akum64qSD2Lm8QFIGl/pub?output=csv'
        
        # Read the sheet directly into a dataframe
        df = pd.read_csv(url)
        
        # Create empty columns for coordinates
        if 'latitude' not in df.columns:
            df['latitude'] = None
        if 'longitude' not in df.columns:
            df['longitude'] = None
        if 'color' not in df.columns:
            df['color'] = [generate_random_color() for _ in range(len(df))]
        
        # Geocode addresses that don't have coordinates
        for idx, row in df.iterrows():
            if pd.isna(row['latitude']) or pd.isna(row['longitude']):
                lat, lon = geocode_address(row['City:'], row['State or Province'], row['Country:'])
                if lat and lon:
                    df.at[idx, 'latitude'] = lat
                    df.at[idx, 'longitude'] = lon
        
        # Drop rows with missing coordinates
        df = df.dropna(subset=['latitude', 'longitude'])
        
        return df
    except Exception as e:
        st.error(f"Error loading sheet: {str(e)}")
        return None

# Load and display the data
df = load_public_sheet_data()
if df is not None:
    # Create the map with custom styling
    st.map(
        df,
        latitude='latitude',
        longitude='longitude',
        color='#FFCC00BF',  # Yellow with 75% opacity
        size=5000,  # Large dot size
        use_container_width=True,
        zoom=2
    )

# Wait for 15 seconds and rerun
time.sleep(10)
st.rerun()