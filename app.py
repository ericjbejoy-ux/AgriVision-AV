import streamlit as st
import pandas as pd
import numpy as np
from deep_translator import GoogleTranslator
from gtts import gTTS
import base64
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="AgriVision (AV)", page_icon="🌱", layout="wide")

# --- TRANSLATION & VOICE LOGIC ---
def translate_and_speak(text, target_lang):
    # 1. Translate
    translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
    
    # 2. Create Voice (Text-to-Speech)
    try:
        tts = gTTS(text=translated, lang=target_lang, slow=False)
        tts.save("response.mp3")
        with open("response.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            audio_html = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(audio_html, unsafe_allow_html=True)
    except:
        pass # Fallback if TTS fails
    return translated

# --- UI HEADER ---
st.title("🌱 AgriVision (AV)")
st.markdown("### *Breaking the Literacy Barrier in Agriculture*")

# --- SIDEBAR / SETTINGS ---
st.sidebar.header("⚙️ Settings / सेटिंग्स")
languages = {"English": "en", "Hindi": "hi", "Tamil": "ta", "Telugu": "te", "Marathi": "mr"}
sel_lang_name = st.sidebar.selectbox("Select Language / भाषा चुनें", list(languages.keys()))
target_code = languages[sel_lang_name]

# --- MAIN INTERFACE ---
st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    st.header("📊 " + GoogleTranslator(target=target_code).translate("Enter Farm Details"))
    
    # Simplified Inputs for Farmers
    temp = st.slider("🌡️ " + GoogleTranslator(target=target_code).translate("Temperature (°C)"), 10, 50, 25)
    rain = st.slider("🌧️ " + GoogleTranslator(target=target_code).translate("Rainfall (mm)"), 200, 3000, 1000)
    nitro = st.number_input("🧪 " + GoogleTranslator(target=target_code).translate("Nitrogen Content (N)"), 0, 150, 70)

with col2:
    st.header("🔮 " + GoogleTranslator(target=target_code).translate("Yield Prediction"))
    
    if st.button("🚀 " + GoogleTranslator(target=target_code).translate("Predict My Yield")):
        # MOCK ML MODEL LOGIC (Replace this with model.predict() later)
        # Yield = (Rainfall * 0.01) + (Nitrogen * 0.05) - (Temp variation)
        result_value = (rain * 0.01) + (nitro * 0.05) - (abs(25-temp) * 0.2)
        
        result_msg = f"Your estimated crop yield is {result_value:.2f} tons per hectare."
        
        # Translate and Speak the result!
        translated_msg = translate_and_speak(result_msg, target_code)
        
        st.success(translated_msg)
        st.metric(label="Predicted Yield", value=f"{result_value:.2f} Tons/Ha")
        
        # Actionable Advice
        if result_value < 12:
            advice = "Warning: Yield is low. Try increasing Nitrogen or checking irrigation."
        else:
            advice = "Great news! Conditions are optimal for a high yield."
        
        st.info(translate_and_speak(advice, target_code))

# --- FOOTER ---
st.divider()
st.caption("AgriVision AV - Empowering every farmer with Data Science.")
