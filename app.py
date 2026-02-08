import streamlit as st
import numpy as np
from deep_translator import GoogleTranslator
from gtts import gTTS
import speech_recognition as sr
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import av
import uuid
import os
import queue

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AgriVision (AV)",
    page_icon="🌱",
    layout="wide"
)

# ---------------- AUDIO QUEUE ----------------
audio_queue = queue.Queue()

class AudioProcessor(AudioProcessorBase):
    def recv(self, frame: av.AudioFrame):
        audio_queue.put(frame)
        return frame

# ---------------- UTILS ----------------
def speak_text(text, lang):
    filename = f"audio_{uuid.uuid4()}.mp3"
    gTTS(text=text, lang=lang).save(filename)
    st.audio(filename)
    os.remove(filename)

def translate_text(text, lang):
    return GoogleTranslator(source="auto", target=lang).translate(text)

def recognize_speech():
    recognizer = sr.Recognizer()
    frames = []

    while not audio_queue.empty():
        frame = audio_queue.get()
        frames.append(frame.to_ndarray())

    if not frames:
        return None

    audio_data = np.concatenate(frames).tobytes()
    audio = sr.AudioData(audio_data, 48000, 2)

    try:
        return recognizer.recognize_google(audio)
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

lang_name = st.sidebar.selectbox("Select Language / भाषा चुनें", list(languages.keys()))
lang_code = languages[lang_name]

# ---------------- MAIN UI ----------------
st.divider()
col1, col2 = st.columns(2)

# ================= INPUT COLUMN =================
with col1:
    st.header("📊 " + translate_text("Enter Farm Details", lang_code))

    st.subheader("🎤 Speak your values")

    webrtc_streamer(
        key="speech",
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
    )

    if st.button("🗣️ Convert Speech to Text"):
        spoken_text = recognize_speech()
        if spoken_text:
            st.success(f"You said: {spoken_text}")
        else:
            st.error("Speech not detected")

    st.subheader("✍️ Manual Input")

    temp = st.slider("🌡️ Temperature (°C)", 10, 50, 25)
    rain = st.slider("🌧️ Rainfall (mm)", 200, 3000, 1000)
    nitro = st.number_input("🧪 Nitrogen Content (N)", 0, 150, 70)

# ================= OUTPUT COLUMN =================
with col2:
    st.header("🔮 " + translate_text("Yield Prediction", lang_code))

    if st.button("🚀 Predict My Yield"):
        yield_val = (rain * 0.01) + (nitro * 0.05) - (abs(25 - temp) * 0.2)

        result = f"Your estimated crop yield is {yield_val:.2f} tons per hectare."
        translated = translate_text(result, lang_code)

        st.success(translated)
        speak_text(translated, lang_code)

        st.metric("Predicted Yield", f"{yield_val:.2f} Tons/Ha")

        if yield_val < 12:
            advice = "Warning: Yield is low. Improve irrigation or nitrogen."
        else:
            advice = "Great news! Conditions are optimal for a high yield."

        translated_advice = translate_text(advice, lang_code)
        st.info(translated_advice)
        speak_text(translated_advice, lang_code)

# ---------------- FOOTER ----------------
st.divider()
st.caption("AgriVision AV — Empowering every farmer with Data Science 🌾")
