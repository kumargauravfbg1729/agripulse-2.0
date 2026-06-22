import streamlit as st
import pickle
import numpy as np
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="AgriPulse AI Dashboard", layout="wide")

def get_live_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    try:
        res = requests.get(url)
        if res.status_code == 200: return res.json().get('current_weather')
    except: return None
    return None

# --- SIDEBAR ---
st.sidebar.title(" Control Panel")
city = st.sidebar.selectbox("Select Target Region", ["Bhopal", "Gorakhpur", "Kota"])

st.sidebar.markdown("---")
st.sidebar.subheader(" Raw Satellite Inputs")
ndvi_input = st.sidebar.slider("NDVI (Vegetation Index)", 0.0, 1.0, 0.5)
dprvic_input = st.sidebar.slider("DpRVIc (Radar)", 0.0, 1.0, 0.3)
svadi_input = st.sidebar.slider("SVADI (Soil Moisture)", 0.0, 1.0, 0.7)
kc_input = st.sidebar.slider("Kc (Crop Coefficient)", 0.0, 1.5, 1.1)

# --- MAIN DASHBOARD ---
st.title(" AgriPulse AI: Precision Irrigation Engine")

locations = {"Bhopal": [23.25, 77.41], "Gorakhpur": [26.76, 83.37], "Kota": [25.21, 75.86]}
lat, lon = locations[city]

tab1, tab2 = st.tabs([" Precision Field Heatmap", " AI Engine & Advisory"])

# TAB 1: FAST HEATMAP
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f" Field Moisture X-Ray: {city} Farm")
        st.caption("Red areas need immediate irrigation. Blue areas have optimal moisture.")
        
        # Simulated Farm Grid Logic based on slider input
        np.random.seed(42) # For stable visual
        base_moisture = svadi_input * 100
        # Create a 10x10 grid with realistic field variations
        farm_grid = base_moisture + np.random.normal(0, 15, (10, 10))
        farm_grid = np.clip(farm_grid, 0, 100) # Keep limits 0-100%
        
        # Plotly Heatmap
        fig = px.imshow(farm_grid, color_continuous_scale='RdYlBu', zmin=0, zmax=100,
                        labels=dict(color="Moisture %"))
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader(" Live Environment")
        weather = get_live_weather(lat, lon)
        if weather:
            st.metric("Temperature", f"{weather.get('temperature')} °C")
            st.metric("Wind Speed", f"{weather.get('windspeed')} km/h")
        else:
            st.warning("Weather API offline.")

# TAB 2: AI INFERENCE
with tab2:
    try:
        with open('crop_identifier_model.pkl', 'rb') as f:
            crop_model = pickle.load(f)
        
        features = np.array([[ndvi_input, dprvic_input, svadi_input, kc_input]])
        
        if st.button(" Run Inference Engine", use_container_width=True):
            pred = crop_model.predict(features)[0]
            mapping = {0: "Rice (Paddy) ", 1: "Wheat (Gehun) ", 2: "Maize (Makka) "}
            st.success(f"**Identified Crop:** {mapping.get(pred, 'Unknown')}")
            
            st.subheader(" Smart Irrigation Logic")
            if pred == 0: st.info("Rice detected. Maintain 10-12 mm water level based on field heatmap.")
            elif pred == 1: st.info("Wheat detected. Apply 4-5 mm controlled irrigation to red zones.")
            else: st.info("Maize detected. Optimal root zone drainage required.")
    except FileNotFoundError:
        st.error("Model missing. Check GitHub.")
