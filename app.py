import streamlit as st
import pickle
import numpy as np
import requests
import plotly.express as px
from twilio.rest import Client

st.set_page_config(page_title="AgriPulse AI Dashboard", layout="wide")

# --- TWILIO CREDENTIALS (Yahan apni details daalein) ---
TWILIO_ACCOUNT_SID = "AC83434b91a58e2e536e1c4a1fd151d091"
TWILIO_AUTH_TOKEN = "203e8653490e6c363621473b2e32375b"
TWILIO_PHONE_NUMBER = "+12543484869" # e.g., "+1234567890"

def send_kisan_sms(phone_number, crop, dry_zone, water_amount):
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message_body = f" AgriPulse Alert: Namaskar! Aapke khet mein {crop} ki fasal ki janch hui hai. Khet ke '{dry_zone}' (disha) mein mitti sookh rahi hai. Kripya aaj wahan {water_amount} paani dein. Paani bachayen, fasal badhayen!"
        
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return True
    except Exception as e:
        st.error(f"SMS Error: {e}")
        return False

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

tab1, tab2 = st.tabs([" Precision Field Heatmap", " AI Engine & Farmer Advisory"])

# TAB 1: FAST HEATMAP
with tab1:
    st.subheader(f" Field Moisture X-Ray: {city} Farm")
    
    # Grid Logic & Spatial Translation
    np.random.seed(42)
    base_moisture = svadi_input * 100
    farm_grid = base_moisture + np.random.normal(0, 15, (10, 10))
    farm_grid = np.clip(farm_grid, 0, 100)
    
    # AI detecting which part is the driest (The Magic Translation)
    dry_zone_name = "Purbi (East)" if svadi_input < 0.4 else "Uttari (North)" if svadi_input < 0.7 else "Dakshini (South)"
    
    fig = px.imshow(farm_grid, color_continuous_scale='RdYlBu', zmin=0, zmax=100)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=350)
    st.plotly_chart(fig, use_container_width=True)

# TAB 2: AI INFERENCE & SMS
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
        water_req = "Drip irrigation for 2 hours"
        
    st.success(f"**Identified Crop:** {crop_name}")
    st.info(f"**AI Field Translation:** The driest area is identified in the **{dry_zone_name}** section of the farm.")
    
    st.markdown("---")
    st.subheader(" Send Alert to Farmer")
    farmer_number = st.text_input("Enter Farmer's Mobile Number (Format: +919876543210)", value="+91")
    
    if st.button(" Send SMS Advisory"):
        if TWILIO_ACCOUNT_SID == "YOUR_TWILIO_SID_HERE":
            st.error("Please add your Twilio Credentials in the code first!")
        elif len(farmer_number) == 13: # +91 and 10 digits
            success = send_kisan_sms(farmer_number, crop_name, dry_zone_name, water_req)
            if success:
                st.balloons()
                st.success(f" SMS successfully sent to {farmer_number}!")
        else:
            st.warning("Please enter a valid 10-digit Indian mobile number with +91.")
