import streamlit as st
import re
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

# ---------------- UTILS ----------------
def translate_text(text, lang):
    return GoogleTranslator(source="auto", target=lang).translate(text)

def speak_text(text, lang):
    filename = f"audio_{uuid.uuid4()}.mp3"
    gTTS(text=text, lang=lang).save(filename)
    with open(filename, "rb") as f:
        audio_bytes = f.read()
        b64 = base64.b64encode(audio_bytes).decode()
    st.markdown(f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}">
        </audio>
    """, unsafe_allow_html=True)
    os.remove(filename)

# -------- SPEECH DATA EXTRACTION --------
def extract_value(text, keywords, default):
    for key in keywords:
        match = re.search(rf"{key}[^0-9]*([0-9]+)", text.lower())
        if match:
            return int(match.group(1))
    return default

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

# ---------------- SPEECH INPUT ----------------
st.subheader("🎤 Speak your farm details")

speech_js = """
<script>
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.lang = 'en-US';
recognition.continuous = false;

function startDictation() {
    recognition.start();
}

recognition.onresult = function(event) {
    const text = event.results[0][0].transcript;
    document.getElementById("speech_output").value = text;
};
</script>

<textarea id="speech_output" rows="2" style="width:100%" 
placeholder="Example: temperature 30, rainfall 1200, nitrogen 60"></textarea>
<br><br>
<button onclick="startDictation()">🎙️ Start Speaking</button>
"""

st.components.v1.html(speech_js, height=180)

spoken_text = st.text_input("Detected Speech (editable)")

# ---------------- ANALYZE SPEECH ----------------
temp = extract_value(spoken_text, ["temperature", "temp"], 25)
rain = extract_value(spoken_text, ["rainfall", "rain"], 1000)
nitro = extract_value(spoken_text, ["nitrogen", "nitro"], 70)

st.divider()
col1, col2 = st.columns(2)

# ================= INPUT =================
with col1:
    st.header("📊 Auto-Extracted Values")

    st.write(f"🌡️ Temperature: **{temp} °C**")
    st.write(f"🌧️ Rainfall: **{rain} mm**")
    st.write(f"🧪 Nitrogen: **{nitro}**")

# ================= OUTPUT =================
with col2:
    st.header("🔮 Yield & Viability")

    if st.button("🚀 Analyze from Speech"):
        yield_val = (rain * 0.01) + (nitro * 0.05) - (abs(25 - temp) * 0.2)

        result_msg = f"Your estimated crop yield is {yield_val:.2f} tons per hectare."
        result_t = translate_text(result_msg, lang_code)

        st.success(result_t)
        speak_text(result_t, lang_code)

        if yield_val < 12:
            advice = "Not suitable for planting. Improve irrigation or soil nutrients."
        else:
            advice = "Suitable for planting. Conditions are favorable for good yield."

        advice_t = translate_text(advice, lang_code)
        st.info(advice_t)
        speak_text(advice_t, lang_code)

# ---------------- FOOTER ----------------
st.divider()
st.caption("AgriVision AV — Speech-driven farm intelligence 🌾")
