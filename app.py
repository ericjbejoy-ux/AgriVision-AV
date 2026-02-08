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

# ---------------- GLOBAL QUEUE ----------------
if "audio_queue" not in st.session_state:
    st.session_state.audio_queue = queue.Queue()

class AudioProcessor(AudioProcessorBase):
    def recv(self, frame: av.AudioFrame):
        st.session_state.audio_queue.put(frame)
        return frame

# ---------------- UTILS ----------------
def translate_text(text, lang):
    return GoogleTranslator(source="auto", target=lang).translate(text)

def speak_text(text, lang):
    filename = f"audio_{uuid.uuid4()}.mp3"
    gTTS(text=text, lang=lang).save(filename)
    st.audio(filename)
    os.remove(filename)

def recognize_speech():
    recognizer = sr.Recognizer()
    frames = []

    while not st.session_state.audio_queue.empty():
        frame = st.session_state.audio_queue.get()
        frames.append(frame.to_ndarray())

    if not frames:
        return None

    audio_np = np.concatenate(frames, axis=1)
    audio_data = audio_np.tobytes()

    audio = sr.AudioData(audio_data, sample_rate=48000, sample_width=2)

    try:
        return recognizer.recognize_google(audio)
    except:
        return None

# ---------------- UI HEADER ----------------
st.title("🌱 AgriVision (AV)")
st.markdown("### *Breaking the Literacy Barrier in Agriculture*")

# ---------------- SIDEBAR ----------------
st.sidebar.header("⚙️ Settings")

languages = {
    "English": "en",
    "Hindi": "hi",
    "Tamil": "ta",
    "Telugu": "te",
    "Marathi": "mr"
}

lang_name = st.sidebar.selectbox("Language", list(languages.keys()))
lang_code = languages[lang_name]

# ---------------- MAIN UI ----------------
st.divider()
col1, col2 = st.columns(2)

# ================= INPUT =================
with col1:
    st.header("📊 " + translate_text("Enter Farm Details", lang_code))

    st.subheader("🎤 Speak now (click Start → talk → Stop)")

    ctx = webrtc_streamer(
        key="mic",
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
        async_processing=True,
    )

    if st.button("🗣️ Convert Speech to Text"):
        if ctx.state.playing:
            st.warning("Please stop recording first")
        else:
            spoken = recognize_speech()
            if spoken:
                st.success(f"You said: {spoken}")
            else:
                st.error("No speech detected")

    st.subheader("✍️ Manual Input")
    temp = st.slider("🌡️ Temperature (°C)", 10, 50, 25)
    rain = st.slider("🌧️ Rainfall (mm)", 200, 3000, 1000)
    nitro = st.number_input("🧪 Nitrogen Content (N)", 0, 150, 70)

# ================= OUTPUT =================
with col2:
    st.header("🔮 " + translate_text("Yield Prediction", lang_code))

    if st.button("🚀 Predict My Yield"):
        result = (rain * 0.01) + (nitro * 0.05) - (abs(25 - temp) * 0.2)

        msg = f"Your estimated crop yield is {result:.2f} tons per hectare."
        translated = translate_text(msg, lang_code)

        st.success(translated)
        speak_text(translated, lang_code)

        st.metric("Predicted Yield", f"{result:.2f} Tons/Ha")

        advice = (
            "Warning: Yield is low. Improve irrigation or nitrogen."
            if result < 12
            else "Great news! Conditions are optimal for a high yield."
        )

        advice_t = translate_text(advice, lang_code)
        st.info(advice_t)
        speak_text(advice_t, lang_code)

# ---------------- FOOTER ----------------
st.divider()
st.caption("AgriVision AV — Empowering every farmer 🌾")
