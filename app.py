import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import urllib.parse

# Page Setup
st.set_page_config(page_title="AgriPulse AI Premium", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .big-alert {
        background-color: #fdf3e7;
        border-left: 6px solid #e74c3c;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# 1. HYBRID DATABASE (Actual Rural Coordinates & Micro-Zones)
# We are using exact coordinates of real agricultural fields now, not city centers.
farm_database = {
    "FARM-MP-42A (Sehore Village)": {
        "lat": 23.2150, "lon": 77.2950, # Real farm location outside Bhopal
        "ndvi": 0.65, "svadi": 0.20, "crop": "Wheat",
        "dry_zone_name": "Dakshini (South)", 
        "dry_bounds": [[23.2140, 77.2940], [23.2150, 77.2960]] # Red zone coordinates (South half)
    },
    "FARM-UP-18B (Basti Village)": {
        "lat": 26.8100, "lon": 82.7500, 
        "ndvi": 0.82, "svadi": 0.65, "crop": "Rice",
        "dry_zone_name": "Purbi (East)",
        "dry_bounds": [[26.8090, 82.7510], [26.8110, 82.7520]] # Red zone coordinates (East half)
    },
    "FARM-RJ-09C (Baran Village)": {
        "lat": 25.1050, "lon": 76.5100, 
        "ndvi": 0.45, "svadi": 0.15, "crop": "Maize",
        "dry_zone_name": "Uttari (North)",
        "dry_bounds": [[25.1060, 76.5090], [25.1070, 76.5110]] # Red zone coordinates (North half)
    }
}

st.title(" AgriPulse AI: Precision Farm Dashboard")

# Top Selection Bar
selected_farm = st.selectbox("Select Specific Farm ID:", list(farm_database.keys()))
data = farm_database[selected_farm]

# Background Calculations
dynamic_kc = (1.25 * data['ndvi']) + 0.2
et0 = 5.2 
deficit = round(max(0, (dynamic_kc * et0) - 0.5), 1)

st.markdown("---")

col1, col2 = st.columns([1.5, 1])

# LEFT COLUMN: Interactive MICRO-LEVEL Map
with col1:
    st.subheader(f" Field Moisture X-Ray: {selected_farm}")
    
    # Folium Map zoomed in closely to the specific farm (Zoom level 17)
    m = folium.Map(location=[data['lat'], data['lon']], zoom_start=17, maptype="satellite")
    
    # 1. Draw the Full Farm Boundary (Green Square)
    farm_bounds = [[data['lat']-0.001, data['lon']-0.001], [data['lat']+0.001, data['lon']+0.001]]
    folium.Rectangle(
        bounds=farm_bounds, 
        color="#27ae60", 
        fill=True, 
        fill_opacity=0.1, 
        tooltip="Full Farm Boundary"
    ).add_to(m)
    
    # 2. Draw the Critical Dry Zone (Red Area based on the database)
    if data['svadi'] < 0.4:
        folium.Rectangle(
            bounds=data['dry_bounds'], 
            color="#e74c3c", 
            fill=True, 
            fill_opacity=0.6, 
            tooltip=f"Critical Stress: {data['dry_zone_name']} Zone"
        ).add_to(m)

    st_folium(m, width=650, height=400)

# RIGHT COLUMN: Premium Analytics
with col2:
    st.subheader(" Farm Analytics")
    g1, g2 = st.columns(2)
    
    with g1:
        fig_health = go.Figure(go.Indicator(
            mode = "gauge+number", value = data['ndvi'] * 10, title = {'text': "Crop Health"},
            gauge = {'axis': {'range': [0, 10]}, 'bar': {'color': "green"}}
        ))
        fig_health.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_health, use_container_width=True)

    with g2:
        fig_moisture = go.Figure(go.Indicator(
            mode = "gauge+number", value = data['svadi'] * 100, number = {'suffix': "%"}, title = {'text': "Moisture"},
            gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#3498db"}}
        ))
        fig_moisture.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_moisture, use_container_width=True)

    # THE BIG ACTIONABLE OUTPUT (Now with specific zone info)
    st.markdown(f"""
    <div class="big-alert">
        <h4 style="margin:0; color:#c0392b;"> CRITICAL ZONE: {data['dry_zone_name'].upper()}</h4>
        <h2 style="margin:0; color:#2c3e50;">Apply {deficit} mm water</h2>
    </div>
    """, unsafe_allow_html=True)

# WhatsApp Integration Button (With Zone Translation)
st.markdown("---")
st.subheader(" Last-Mile Advisory Delivery")
col_w1, col_w2 = st.columns([1, 2])
with col_w1:
    farmer_number = st.text_input("Farmer's WhatsApp No:", value="9876543210")
with col_w2:
    st.write("") 
    st.write("")
    # THE SMART MESSAGE
    whatsapp_msg = f" *AgriPulse AI Alert*\nNamaskar! Aapke khet ({selected_farm}) ki jaanch hui hai.\n\n Khet ke *{data['dry_zone_name']}* hisse mein mitti sookh rahi hai.\n Kripya aaj wahi par *{deficit} mm* paani dein. Baaki khet theek hai.\n\nPaani bachayen, fasal badhayen!"
    
    whatsapp_url = f"https://wa.me/91{farmer_number}?text={urllib.parse.quote(whatsapp_msg)}"
    st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="display: inline-block; padding: 12px 24px; background-color: #25D366; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">💬 Send Zone-Specific WhatsApp Alert</a>', unsafe_allow_html=True)
