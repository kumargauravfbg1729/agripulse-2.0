import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import urllib.parse

# Page Setup
st.set_page_config(page_title="AgriPulse AI Premium", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS to make it look exactly like your Architecture Diagram
st.markdown("""
<style>
    .big-alert {
        background-color: #fdf3e7;
        border-left: 6px solid #f39c12;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# 1. HYBRID DATABASE (Crash-Proof Data)
farm_database = {
    "FARM-MP-01 (Bhopal)": {"lat": 23.2599, "lon": 77.4126, "ndvi": 0.75, "svadi": 0.20, "crop": "Wheat"},
    "FARM-UP-02 (Gorakhpur)": {"lat": 26.7606, "lon": 83.3732, "ndvi": 0.82, "svadi": 0.65, "crop": "Rice"},
    "FARM-RJ-03 (Kota)": {"lat": 25.2138, "lon": 75.8648, "ndvi": 0.45, "svadi": 0.15, "crop": "Maize"}
}

st.title(" AgriPulse AI: Farmer's Advisory Dashboard")

# Top Selection Bar
selected_farm = st.selectbox(" Select Target Farm:", list(farm_database.keys()))
data = farm_database[selected_farm]

# Background Calculations (From your PDF)
dynamic_kc = (1.25 * data['ndvi']) + 0.2
et0 = 5.2 # Simulated Weather ET0
deficit = round(max(0, (dynamic_kc * et0) - 0.5), 1) # Deficit Math

st.markdown("---")

# Main Dashboard Layout (Matches your diagram)
col1, col2 = st.columns([1.5, 1])

# LEFT COLUMN: Interactive Map
with col1:
    st.subheader(" Precision Field Heatmap")
    # Folium Map
    m = folium.Map(location=[data['lat'], data['lon']], zoom_start=15, tiles="CartoDB positron")
    # Adding a simulated heatmap zone (Red for dry, Green for wet)
    zone_color = "red" if data['svadi'] < 0.4 else "green"
    folium.CircleMarker(
        location=[data['lat'], data['lon']],
        radius=50,
        color=zone_color,
        fill=True,
        fill_color=zone_color,
        fill_opacity=0.4,
        popup="Moisture Stress Zone"
    ).add_to(m)
    st_folium(m, width=650, height=400)

# RIGHT COLUMN: Premium Analytics (Gauge Charts & Alerts)
with col2:
    st.subheader(" Farm Analytics")
    
    # Row for Speedometers (Gauges)
    g1, g2 = st.columns(2)
    
    with g1:
        # Yield Health Score (NDVI)
        fig_health = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = data['ndvi'] * 10,
            title = {'text': "Yield Health Score"},
            gauge = {'axis': {'range': [0, 10]}, 'bar': {'color': "green"}}
        ))
        fig_health.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_health, use_container_width=True)

    with g2:
        # Current Moisture Level (SVADI)
        fig_moisture = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = data['svadi'] * 100,
            number = {'suffix': "%"},
            title = {'text': "Current Moisture"},
            gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#3498db"}}
        ))
        fig_moisture.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_moisture, use_container_width=True)

    # THE BIG ACTIONABLE OUTPUT (Matches Diagram exactly)
    st.markdown(f"""
    <div class="big-alert">
        <h3 style="margin:0; color:#d35400;"> REQUIRED IRRIGATION:</h3>
        <h1 style="margin:0; color:#2c3e50;">{deficit} mm for next 8 days</h1>
    </div>
    """, unsafe_allow_html=True)

# BOTTOM SECTION: 8-Day Forecast Bar Chart
st.markdown("---")
st.subheader(" 8-Day Rainfall Forecast")

# Simulated Forecast Data
forecast_data = pd.DataFrame({
    "Day": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7", "Day 8"],
    "Rainfall (mm)": [0, 2, 0, 15, 30, 5, 0, 0]
})

fig_bar = px.bar(forecast_data, x="Day", y="Rainfall (mm)", color_discrete_sequence=['#3498db'])
fig_bar.update_layout(height=250, margin=dict(l=0, r=0, t=10, b=0))
st.plotly_chart(fig_bar, use_container_width=True)

# WhatsApp Integration Button
st.markdown("---")
col_w1, col_w2 = st.columns([1, 2])
with col_w1:
    farmer_number = st.text_input("Farmer's WhatsApp No:", value="9876543210")
with col_w2:
    st.write("") # Spacing
    st.write("")
    whatsapp_msg = f"🌾 *AgriPulse AI*\nAapke {data['crop']} khet ({selected_farm}) mein agle 8 din ke liye *{deficit} mm* paani ki zarurat hai. Kripya dhyan dein!"
    whatsapp_url = f"https://wa.me/91{farmer_number}?text={urllib.parse.quote(whatsapp_msg)}"
    
    st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="display: inline-block; padding: 12px 24px; background-color: #25D366; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">💬 Send Direct WhatsApp Alert to Farmer</a>', unsafe_allow_html=True)
