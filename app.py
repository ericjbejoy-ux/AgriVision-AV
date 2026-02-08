import streamlit as st
import pandas as pd
import numpy as np
from deep_translator import GoogleTranslator
from gtts import gTTS
import speech_recognition as sr
import uuid
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AgriVision (AV)",
    page_icon="🌱",
    layout="wide"
)

# ---------------- UTILS ----------------
def speak_text(text, lang):
    """Generate single safe audio output (no collision)"""
    filename = f"audio_{uuid.uuid4()}.mp3"
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)

    with open(filename, "rb") as audio:
        st.audio(audio.read(), format="audio/mp3")

    os.remove(filename)


def translate_text(text, target_lang):
    return GoogleTranslator(source="auto", target=target_lang).translate(text)


def speech_to_text(audio_file):
    """Convert uploaded speech to text"""
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    try:
        return r.recognize_google(audio)
    except:
        return None


# ---------------- UI HEADER ----------------
st.title("🌱 AgriVision (AV)")
st.markdown("### *Breaking the Literacy Barrier in Agriculture*")

# ---------------- SIDEBAR ----------------
st.sidebar.header("⚙️ Settings / सेटिंग्स")

languages = {
    "English": "en",
    "Hindi": "hi",
    "Tamil": "ta",
    "Telugu": "te",
    "Marathi": "mr"
}

sel_lang = st.sidebar.selectbox("Select Language / भाषा चुनें", list(languages.keys()))
lang_code = languages[sel_lang]

# ---------------- MAIN UI ----------------
st.divider()
col1, col2 = st.columns(2)

# ================= INPUT COLUMN =================
with col1:
    st.header("📊 " + translate_text("Enter Farm Details", lang_code))

    st.subheader("🎤 Voice Input (Optional)")
    audio_file = st.file_uploader("Upload voice (WAV format)", type=["wav"])

    spoken_text = ""
    if audio_file:
        spoken_text = speech_to_text(audio_file)
        if spoken_text:
            st.success(f"Detected Speech: {spoken_text}")
        else:
            st.error("Could not recognize speech")

    st.subheader("✍️ Manual Input")

    temp = st.slider(
        "🌡️ " + translate_text("Temperature (°C)", lang_code),
        10, 50, 25
    )

    rain = st.slider(
        "🌧️ " + translate_text("Rainfall (mm)", lang_code),
        200, 3000, 1000
    )

    nitro = st.number_input(
        "🧪 " + translate_text("Nitrogen Content (N)", lang_code),
        0, 150, 70
    )

# ================= OUTPUT COLUMN =================
with col2:
    st.header("🔮 " + translate_text("Yield Prediction", lang_code))

    if st.button("🚀 " + translate_text("Predict My Yield", lang_code)):

        # ---- MOCK MODEL ----
        result = (rain * 0.01) + (nitro * 0.05) - (abs(25 - temp) * 0.2)

        result_text = f"Your estimated crop yield is {result:.2f} tons per hectare."
        translated_result = translate_text(result_text, lang_code)

        st.success(translated_result)
        speak_text(translated_result, lang_code)

        st.metric("Predicted Yield", f"{result:.2f} Tons/Ha")

        # ---- ADVICE ----
        if result < 12:
            advice = "Warning: Yield is low. Try increasing Nitrogen or improving irrigation."
        else:
            advice = "Great news! Conditions are optimal for a high yield."

        translated_advice = translate_text(advice, lang_code)
        st.info(translated_advice)
        speak_text(translated_advice, lang_code)

# ---------------- FOOTER ----------------
st.divider()
st.caption("AgriVision AV — Empowering every farmer with Data Science 🌾")
