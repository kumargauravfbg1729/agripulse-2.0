import streamlit as st
import pickle
import numpy as np
import requests
import plotly.express as px
import urllib.parse  # Naya module jo message ko WhatsApp link mein badlega

st.set_page_config(page_title="AgriPulse AI Dashboard", layout="wide")

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

tab1, tab2 = st.tabs([" Precision Field Heatmap", " AI Engine & WhatsApp Advisory"])

# TAB 1: FAST HEATMAP
with tab1:
    st.subheader(f" Field Moisture X-Ray: {city} Farm")
    
    np.random.seed(42)
    base_moisture = svadi_input * 100
    farm_grid = base_moisture + np.random.normal(0, 15, (10, 10))
    farm_grid = np.clip(farm_grid, 0, 100)
    
    dry_zone_name = "Purbi (East)" if svadi_input < 0.4 else "Uttari (North)" if svadi_input < 0.7 else "Dakshini (South)"
    
    fig = px.imshow(farm_grid, color_continuous_scale='RdYlBu', zmin=0, zmax=100)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=350)
    st.plotly_chart(fig, use_container_width=True)

# TAB 2: AI INFERENCE & DIRECT WHATSAPP
with tab2:
    st.subheader("AI Prediction Engine & Advisory")
    
    # Heuristic Engine
    if svadi_input >= 0.6 and ndvi_input > 0.4:
        crop_name = "Rice (Dhaan)"
        water_req = "10-12 mm"
    elif 0.3 <= svadi_input < 0.6:
        crop_name = "Wheat (Gehun)"
        water_req = "4-5 mm"
    else:
        crop_name = "Maize (Makka)"
        water_req = "2 ghante Drip irrigation"
        
    st.success(f"**Identified Crop:** {crop_name}")
    st.info(f"**AI Field Translation:** Mitti khet ke **{dry_zone_name}** hisse mein sookh rahi hai.")
    
    st.markdown("---")
    st.subheader(" Send Free Alert on WhatsApp")
    
    # Farmer ka number lene ke liye (Bina +91 ke)
    farmer_number = st.text_input("Enter Farmer's 10-digit WhatsApp Number:", value="9876543210")
    
    # Message Ban banana
    whatsapp_msg = f" *AgriPulse AI Alert*\nNamaskar! Aapke khet mein {crop_name} ki janch hui hai.\n Khet ke *{dry_zone_name}* hisse mein mitti sookh rahi hai.\n Kripya aaj wahan *{water_req}* paani dein.\nPaani bachayen, fasal badhayen!"
    
    # Message ko URL format mein encode karna
    encoded_msg = urllib.parse.quote(whatsapp_msg)
    
    # WhatsApp ka direct link banana
    whatsapp_url = f"https://wa.me/91{farmer_number}?text={encoded_msg}"
    
    # Ek sundar sa WhatsApp Button lagana (HTML ke zariye)
    if len(farmer_number) == 10:
        st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="display: inline-block; padding: 12px 20px; background-color: #25D366; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">💬 Send to Kisan on WhatsApp</a>', unsafe_allow_html=True)
    else:
        st.warning("Please enter a valid 10-digit number.")
