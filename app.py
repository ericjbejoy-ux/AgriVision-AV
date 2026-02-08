import streamlit as st
import re
import pandas as pd
from deep_translator import GoogleTranslator
from gtts import gTTS
import uuid
import base64
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AgriVision (AV)",
    page_icon="🌱",
    layout="wide"
)

# ---------------- SESSION STATE INIT ----------------
defaults = {
    "temp": 25,
    "rain": 1000,
    "nitro": 70,
    "speech_text": "",
    "data_table": pd.DataFrame(columns=["Temperature", "Rainfall", "Nitrogen"])
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------- UTILS ----------------
def translate_text(text, lang):
    return GoogleTranslator(source="auto", target=lang).translate(text)

def speak_text(text, lang):
    filename = f"audio_{uuid.uuid4()}.mp3"
    gTTS(text=text, lang=lang).save(filename)

    with open(filename, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}">
        </audio>
        """,
        unsafe_allow_html=True
    )
    os.remove(filename)

def extract_value(text, keywords, default):
    for key in keywords:
        match = re.search(rf"{key}[^0-9]*([0-9]+)", text.lower())
        if match:
            return int(match.group(1))
    return default

# ---------------- HEADER ----------------
st.title("🌱 AgriVision (AV)")
st.markdown("### *Speech → Data → Decision Support for Farmers*")

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
    document.getElementById("speech_output").value =
        event.results[0][0].transcript;
};
</script>

<textarea id="speech_output" rows="2" style="width:100%"
placeholder="Example: temperature 30 rainfall 1200 nitrogen 60"></textarea>
<br><br>
<button onclick="startDictation()">🎙️ Start Speaking</button>
"""

st.components.v1.html(speech_js, height=180)

# 👇 this already existed – we keep it
spoken_text = st.text_input("Detected Speech (editable)", st.session_state.speech_text)

# ---------------- STORE SPEECH DATA BUTTON ----------------
if st.button("📥 Store Speech Data"):
    # ✅ ONLY NEW LINE: move spoken text into session
    st.session_state.speech_text = spoken_text

    temp = extract_value(
        st.session_state.speech_text,
        ["temperature", "temp"],
        st.session_state.temp
    )
    rain = extract_value(
        st.session_state.speech_text,
        ["rainfall", "rain"],
        st.session_state.rain
    )
    nitro = extract_value(
        st.session_state.speech_text,
        ["nitrogen", "nitro"],
        st.session_state.nitro
    )

    # update sliders
    st.session_state.temp = temp
    st.session_state.rain = rain
    st.session_state.nitro = nitro

    # store into table
    st.session_state.data_table = pd.concat(
        [
            st.session_state.data_table,
            pd.DataFrame([{
                "Temperature": temp,
                "Rainfall": rain,
                "Nitrogen": nitro
            }])
        ],
        ignore_index=True
    )

    st.success("Speech data stored and applied")

# ---------------- DATA TABLE ----------------
st.subheader("📋 Captured Farm Data")
st.dataframe(st.session_state.data_table, use_container_width=True)

# ---------------- MAIN UI ----------------
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.header("📊 Farm Parameters")

    temp = st.slider(
        "🌡️ Temperature (°C)",
        10, 50,
        st.session_state.temp
    )

    rain = st.slider(
        "🌧️ Rainfall (mm)",
        200, 3000,
        st.session_state.rain
    )

    nitro = st.number_input(
        "🧪 Nitrogen Content",
        0, 150,
        st.session_state.nitro
    )

    st.session_state.temp = temp
    st.session_state.rain = rain
    st.session_state.nitro = nitro

with col2:
    st.header("🔮 Yield Prediction")

    if st.button("🚀 Predict"):
        yield_val = (rain * 0.01) + (nitro * 0.05) - (abs(25 - temp) * 0.2)

        if yield_val < 12:
            advice = "Not suitable for planting. Improve irrigation or soil nutrients."
        else:
            advice = "Suitable for planting. Conditions are favorable."

        result = f"Estimated crop yield is {yield_val:.2f} tons per hectare."

        st.success(translate_text(result, lang_code))
        st.info(translate_text(advice, lang_code))

        speak_text(
            translate_text(f"{result}. {advice}", lang_code),
            lang_code
        )

# ---------------- FOOTER ----------------
st.divider()
st.caption("AgriVision AV — Voice-enabled decision support for farmers 🌾")
