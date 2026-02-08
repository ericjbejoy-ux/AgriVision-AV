import streamlit as st
import pandas as pd
import joblib
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import base64

# --- CONFIGURATION ---
st.set_page_config(page_title="AgriVision-AV", page_icon="🌱", layout="wide")

# Load Model and Data
@st.cache_resource
def load_resources():
    model = joblib.load('crop_model.pkl')
    soil_db = pd.read_csv('processed_nutrients.csv')
    return model, soil_db

try:
    model, soil_db = load_resources()
except:
    st.error("Error: Ensure 'crop_model.pkl' and 'processed_nutrients.csv' are in the folder.")
    st.stop()

# --- SESSION STATE FOR VOICE ---
if 'temp_val' not in st.session_state:
    st.session_state.temp_val = 25.0
if 'rain_val' not in st.session_state:
    st.session_state.rain_val = 1000.0

# --- UI HEADER ---
st.title("🌱 AgriVision-AV: Smart Crop Predictor")
st.markdown("---")

# --- STEP 1: REGIONAL SELECTION ---
col_a, col_b = st.columns([1, 1])

with col_a:
    st.subheader("1. Select Region")
    state_list = soil_db['State'].unique()
    selected_state = st.selectbox("Choose your State/UT", state_list)
    
    # Auto-fetch soil data
    state_data = soil_db[soil_db['State'] == selected_state].iloc[0]
    n_val = state_data['Nitrogen']
    p_val = state_data['Phosphorus']
    k_val = state_data['Potassium']

    # Display Soil Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Nitrogen", f"{n_val}")
    m2.metric("Phosphorus", f"{p_val}")
    m3.metric("Potassium", f"{k_val}")

# --- STEP 2: VOICE & WEATHER INPUTS ---
with col_b:
    st.subheader("2. Weather Parameters")
    
    # Voice Input Simulation (For Hackathon Demo)
    voice_input = st.text_input("🎙️ Voice Command (e.g., 'Set rainfall to 1200')")
    
    if voice_input:
        nums = [float(s) for s in voice_input.split() if s.replace('.','',1).isdigit()]
        text = voice_input.lower()
        if "rain" in text and nums:
            st.session_state.rain_val = nums[0]
            st.toast(f"Rainfall updated to {nums[0]}mm", icon="🌧️")
        if "temp" in text and nums:
            st.session_state.temp_val = nums[0]
            st.toast(f"Temperature updated to {nums[0]}°C", icon="🌡️")

    temp = st.slider("Temperature (°C)", 10.0, 50.0, key="temp_val")
    rain = st.slider("Rainfall (mm)", 200.0, 3000.0, key="rain_val")

# --- STEP 3: PREDICTION ---
st.markdown("---")
if st.button("🚀 Predict Optimal Yield", use_container_width=True):
    # Features must match the training order: N, P, K, Temp, Rain
    input_features = [[n_val, p_val, k_val, temp, rain]]
    prediction = model.predict(input_features)[0]
    
    st.balloons()
    
    # Results Display
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.success(f"### Predicted Yield: {prediction:.2f} Tons/Hectare")
        st.write(f"Based on historical soil data from **{selected_state}** and your specified weather conditions.")
    
    # Multilingual Audio Output (The "AV" part)
    output_text = f"The predicted yield for {selected_state} is {prediction:.2f} tons per hectare."
    # Translate for local impact
    translated = GoogleTranslator(source='auto', target='hi').translate(output_text)
    
    tts = gTTS(text=translated, lang='hi')
    tts.save("result.mp3")
    
    with res_col2:
        st.write("🔊 **Audio Report (Hindi):**")
        audio_file = open("result.mp3", "rb")
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio/mp3')
