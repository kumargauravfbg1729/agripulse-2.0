import streamlit as st
import pickle
import numpy as np

st.title(" AgriPulse 2.0: AI Crop Inference Engine")

# Sliders for Judges to test the data
st.sidebar.header(" Raw Satellite & Sensor Inputs")
ndvi_input = st.sidebar.slider("NDVI (Vegetation Index)", 0.0, 1.0, 0.5)
dprvic_input = st.sidebar.slider("DpRVIc (Radar Backscatter)", 0.0, 1.0, 0.3)
svadi_input = st.sidebar.slider("SVADI (Soil Moisture Index)", 0.0, 1.0, 0.7)
kc_input = st.sidebar.slider("Kc (Crop Coefficient)", 0.0, 1.5, 1.1)

# AI Inference Block
try:
    with open('crop_identifier_model.pkl', 'rb') as f:
        crop_model = pickle.load(f)
        
    input_features = np.array([[ndvi_input, dprvic_input, svadi_input, kc_input]])

    if st.button(" Run AI Crop Identification"):
        # Real-time Prediction
        prediction_encoded = crop_model.predict(input_features)[0]
        probabilities = crop_model.predict_proba(input_features)[0]
        
        crop_mapping = {0: "Rice (Paddy) ", 1: "Wheat (Gehun) ", 2: "Maize (Makka) "}
        detected_crop = crop_mapping.get(prediction_encoded, "Unknown Data")
        
        # Display Outputs
        st.subheader(" Backend Model Output")
        st.success(f"**Scientifically Identified Crop:** {detected_crop}")
        
        # Confidence Levels
        st.write(f"**AI Confidence Level:** Rice ({probabilities[0]:.2%}), Wheat ({probabilities[1]:.2%}), Maize ({probabilities[2]:.2%})")
        
        # Actionable Advisory
        st.subheader("Smart Irrigation Advisory")
        if prediction_encoded == 0:
            st.info("Advisory: Rice signature detected. Maintain a 10-12 mm water level based on the current high SVADI profile.")
        elif prediction_encoded == 1:
            st.info("Advisory: Wheat signature detected. 4-5 mm controlled irrigation recommended for current growth stage.")
        else:
            st.info("Advisory: Maize signature detected. Optimal root zone drainage required. Avoid over-watering.")

except FileNotFoundError:
    st.error("Model file 'crop_identifier_model.pkl' not found. Please wait for GitHub to sync.")
