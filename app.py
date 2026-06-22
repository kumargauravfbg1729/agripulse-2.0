import streamlit as st
import pickle
import numpy as np
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium

# PAGE CONFIGURATION (Professional Wide Layout)
st.set_page_config(page_title="AgriPulse AI Dashboard", layout="wide")

# WEATHER FETCH FUNCTION (Using Open-Meteo - No API Key Needed!)
def get_live_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('current_weather')
    except Exception as e:
        return None
    return None

# --- SIDEBAR (Control Panel) ---
st.sidebar.title(" Control Panel")
city = st.sidebar.selectbox("Select Target Region", ["Bhopal", "Gorakhpur", "Kota"])

st.sidebar.markdown("---")
st.sidebar.subheader(" Raw Satellite Data Inputs")
ndvi_input = st.sidebar.slider("NDVI (Vegetation Index)", 0.0, 1.0, 0.5)
dprvic_input = st.sidebar.slider("DpRVIc (Radar Backscatter)", 0.0, 1.0, 0.3)
svadi_input = st.sidebar.slider("SVADI (Soil Moisture)", 0.0, 1.0, 0.7)
kc_input = st.sidebar.slider("Kc (Crop Coefficient)", 0.0, 1.5, 1.1)

# --- MAIN DASHBOARD ---
st.title(" AgriPulse AI Dashboard")
st.markdown("*Cloud-Agnostic Precision Irrigation & Remote Sensing Engine*")

# --- TABS FOR UI ORGANIZATION ---
tab1, tab2 = st.tabs([" Spatial View & Environment", "AI Engine & Analytics"])

# Location Data
locations = {
    "Bhopal": [23.2599, 77.4126], 
    "Gorakhpur": [26.7606, 83.3732], 
    "Kota": [25.2138, 75.8648]
}
lat, lon = locations[city]

# TAB 1: Interactive Map & Live Weather
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"Satellite View: {city}")
        # Folium Interactive Map
        m = folium.Map(location=[lat, lon], zoom_start=11, tiles="CartoDB positron")
        folium.Marker([lat, lon], popup=f"{city} Farm Area", icon=folium.Icon(color="green", icon="leaf")).add_to(m)
        st_folium(m, width=700, height=400)

    with col2:
        st.subheader(" Live Environment Data")
        weather_data = get_live_weather(lat, lon)
        
        if weather_data:
            temp = weather_data.get('temperature')
            windspeed = weather_data.get('windspeed')
            
            st.metric(label="Current Temperature", value=f"{temp} °C")
            st.metric(label="Wind Speed", value=f"{windspeed} km/h")
            st.info("Data synced via Open-Meteo API")
        else:
            st.warning("Weather API currently offline.")

# TAB 2: The Core Machine Learning Engine
with tab2:
    st.subheader("AI Prediction Engine & Advisory")
    try:
        with open('crop_identifier_model.pkl', 'rb') as f:
            crop_model = pickle.load(f)
        
        input_features = np.array([[ndvi_input, dprvic_input, svadi_input, kc_input]])
        
        if st.button(" Run AI Engine", use_container_width=True):
            pred = crop_model.predict(input_features)[0]
            probs = crop_model.predict_proba(input_features)[0]
            mapping = {0: "Rice (Paddy) ", 1: "Wheat (Gehun) ", 2: "Maize (Makka) "}
            
            st.success(f"**Identified Crop in {city}:** {mapping.get(pred, 'Unknown')}")
            st.write(f"**Confidence:** Rice ({probs[0]:.2%}), Wheat ({probs[1]:.2%}), Maize ({probs[2]:.2%})")
            
            st.subheader(" Smart Irrigation Logic")
            if pred == 0:
                st.info("Rice detected. Maintain 10-12 mm water level based on high SVADI profile.")
            elif pred == 1:
                st.info("Wheat detected. 4-5 mm controlled irrigation recommended.")
            else:
                st.info("Maize detected. Optimal root zone drainage required.")
                
    except FileNotFoundError:
        st.error("Model file missing. Please check GitHub repository.")
