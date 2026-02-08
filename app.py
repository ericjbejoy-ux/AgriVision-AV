import streamlit as st
import numpy as np
from deep_translator import GoogleTranslator
from gtts import gTTS
import uuid
import os
import base64

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AgriVision (AV)",
    page_icon="🌱",
    layout="wide"
)

# ---------------- SESSION STATE INIT ----------------
if "language" not in st.session_state:
    st.session_state.language = "English"

# ---------------- UTILS ----------------
def translate_text(text, lang):
    return GoogleTranslator(source="auto", target=lang).translate(text)

def speak_text(text, lang):
    filename = f"audio_{uuid.uuid4()}.mp3"
    gTTS(text=text, lang=lang).save(filename)

    with open(filename, "rb") as f:
        audio_bytes = f.read()
        b64 = base64.b64encode(audio_bytes).decode()

    audio_html = f"""
    <audio autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)
    os.remove(filename)

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

lang_name = st.sidebar.selectbox(
    "Language",
    options=list(languages.keys()),
    index=list(languages.keys()).index(st.session_state.language),
    key="language_selector"
)

st.session_state.language = lang_name
lang_code = languages[lang_name]

# ---------------- SPEECH INPUT (JS – SAFE) ----------------
st.subheader("🎤 Speak your farm details")

speech_js = """
<script>
var recognition;

function startDictation() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("Speech recognition not supported in this browser");
        return;
    }

    recognition = new webkitSpeechRecognition();
    recognition.lang = 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = function(event) {
        const text = event.results[0][0].transcript;
        document.getElementById("speech_output").value = text;
    };

    recognition.start();
}
</script>

<textarea id="speech_output" rows="2" style="width:100%" placeholder="Your speech will appear here..."></textarea>
<br><br>
<button onclick="startDictation()">🎙️ Start Speaking</button>
"""

st.components.v1.html(speech_js, height=180)

spoken_text = st.text_input("Detected Speech (editable)", "")

# ---------------- MAIN UI ----------------
st.divider()
col1, col2 = st.columns(2)

# ================= INPUT =================
with col1:
    st.header("📊 " + translate_text("Enter Farm Details", lang_code))

    temp = st.slider("🌡️ Temperature (°C)", 10, 50, 25)
    rain = st.slider("🌧️ Rainfall (mm)", 200, 3000, 1000)
    nitro = st.number_input("🧪 Nitrogen Content (N)", 0, 150, 70)

# ================= OUTPUT =================
with col2:
    st.header("🔮 " + translate_text("Yield & Viability", lang_code))

    if st.button("🚀 Predict"):
        yield_val = (rain * 0.01) + (nitro * 0.05) - (abs(25 - temp) * 0.2)

        result_msg = f"Your estimated crop yield is {yield_val:.2f} tons per hectare."
        result_t = translate_text(result_msg, lang_code)

        st.success(result_t)
        speak_text(result_t, lang_code)

        st.metric("Predicted Yield", f"{yield_val:.2f} Tons/Ha")

        if yield_val < 12:
            advice = "Not suitable for planting. Improve irrigation or soil nutrients."
        else:
            advice = "Suitable for planting. Conditions are favorable for good yield."

        advice_t = translate_text(advice, lang_code)
        st.info(advice_t)
        speak_text(advice_t, lang_code)

# ---------------- FOOTER ----------------
st.divider()
st.caption("AgriVision AV — Voice-enabled decision support for farmers 🌾")
