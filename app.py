import streamlit as st
import re
import pandas as pd
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

# ---------------- SESSION STATE ----------------
if "temp" not in st.session_state:
    st.session_state.temp = 25
if "rain" not in st.session_state:
    st.session_state.rain = 1000
if "nitro" not in st.session_state:
    st.session_state.nitro = 70
if "speech_raw" not in st.session_state:
    st.session_state.speech_raw = ""
if "speech_stored" not in st.session_state:
    st.session_state.speech_stored = ""
if "data_table" not in st.session_state:
    st.session_state.data_table = pd.DataFrame(
        columns=["Temperature", "Rainfall", "Nitrogen"]
    )

# ---------------- UTILS ----------------
def speak_text(text):
    filename = f"audio_{uuid.uuid4()}.mp3"
    gTTS(text=text, lang="en").save(filename)

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
st.markdown("### *Speech → Data → Smart Farming Decisions*")

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
    document.getElementById("speech_box").value =
        event.results[0][0].transcript;
};
</script>

<textarea id="speech_box" rows="2" style="width:100%"
placeholder="Example: temperature 30 rainfall 1200 nitrogen 60"></textarea>
<br><br>
<button onclick="startDictation()">🎙️ Start Speaking</button>
"""

st.components.v1.html(speech_js, height=180)

# Raw speech input (manual sync)
st.session_state.speech_raw = st.text_input(
    "Raw Speech Input",
    st.session_state.speech_raw
)

# ---------------- STORE BUTTON ----------------
if st.button("📥 Store Speech Data"):
    st.session_state.speech_stored = st.session_state.speech_raw

    temp = extract_value(
        st.session_state.speech_stored,
        ["temperature", "temp"],
        st.session_state.temp
    )
    rain = extract_value(
        st.session_state.speech_stored,
        ["rainfall", "rain"],
        st.session_state.rain
    )
    nitro = extract_value(
        st.session_state.speech_stored,
        ["nitrogen", "nitro"],
        st.session_state.nitro
    )

    # Update session state
    st.session_state.temp = temp
    st.session_state.rain = rain
    st.session_state.nitro = nitro

    # Store in table
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

    st.success("Speech data stored and applied successfully!")

# ---------------- DETECTED SPEECH ----------------
st.subheader("📝 Detected Speech (Stored)")
st.text_area(
    "Detected Speech",
    st.session_state.speech_stored,
    height=70
)

# ---------------- DATA TABLE ----------------
st.subheader("📋 Stored Farm Data")
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

        st.success(result)
        st.info(advice)

        speak_text(f"{result}. {advice}")

# ---------------- FOOTER ----------------
st.divider()
st.caption("AgriVision AV — Controlled voice-to-data farming system 🌾")
