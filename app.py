import streamlit as st
import pandas as pd
import re
import uuid
import base64
import os
from gtts import gTTS

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AgriVision (AV)",
    page_icon="🌱",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "data_table" not in st.session_state:
    st.session_state.data_table = pd.DataFrame(
        columns=["Temperature", "Rainfall", "Nitrogen"]
    )

if "temp" not in st.session_state:
    st.session_state.temp = 25
if "rain" not in st.session_state:
    st.session_state.rain = 1000
if "nitro" not in st.session_state:
    st.session_state.nitro = 60

# ---------------- FUNCTIONS ----------------
def extract_number(text, keyword, default):
    """
    Extracts number AFTER a keyword
    Example: 'temperature 32' → 32
    """
    pattern = rf"{keyword}[^0-9]*([0-9]+)"
    match = re.search(pattern, text.lower())
    return int(match.group(1)) if match else default

def speak(text):
    filename = f"{uuid.uuid4()}.mp3"
    gTTS(text=text, lang="en").save(filename)

    with open(filename, "rb") as f:
        audio_bytes = f.read()
        b64 = base64.b64encode(audio_bytes).decode()

    st.markdown(
        f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}">
        </audio>
        """,
        unsafe_allow_html=True
    )
    os.remove(filename)

# ---------------- HEADER ----------------
st.title("🌱 AgriVision (AV)")
st.markdown("### Speech → Data → Storage → Analysis")

# ---------------- SPEECH INPUT ----------------
st.subheader("🎤 Speak Your Farm Data")

speech_html = """
<script>
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.lang = 'en-US';

function startSpeech(){
    recognition.start();
}

recognition.onresult = function(event){
    document.getElementById("speechBox").value =
        event.results[0][0].transcript;
};
</script>

<textarea id="speechBox" rows="2" style="width:100%"
placeholder="Example: temperature 32 rainfall 1450 nitrogen 60"></textarea>
<br><br>
<button onclick="startSpeech()">🎙 Start Speaking</button>
"""

st.components.v1.html(speech_html, height=180)

spoken_text = st.text_input("Detected Speech (editable)")

# ---------------- SPEECH → DATA ----------------
if st.button("📥 Store Speech Data") and spoken_text:
    temp = extract_number(spoken_text, "temperature", st.session_state.temp)
    rain = extract_number(spoken_text, "rainfall", st.session_state.rain)
    nitro = extract_number(spoken_text, "nitrogen", st.session_state.nitro)

    new_row = {
        "Temperature": temp,
        "Rainfall": rain,
        "Nitrogen": nitro
    }

    st.session_state.data_table = pd.concat(
        [st.session_state.data_table, pd.DataFrame([new_row])],
        ignore_index=True
    )

    # Update sliders from stored data
    st.session_state.temp = temp
    st.session_state.rain = rain
    st.session_state.nitro = nitro

    st.success("Speech data stored successfully ✔")

# ---------------- DATA TABLE ----------------
st.subheader("📋 Stored Speech Data")
st.dataframe(st.session_state.data_table, use_container_width=True)

st.divider()
col1, col2 = st.columns(2)

# ---------------- INPUT SLIDERS ----------------
with col1:
    st.header("📊 Farm Parameters")

    temp = st.slider("🌡 Temperature (°C)", 10, 50, st.session_state.temp)
    rain = st.slider("🌧 Rainfall (mm)", 200, 3000, st.session_state.rain)
    nitro = st.slider("🧪 Nitrogen", 0, 150, st.session_state.nitro)

    st.session_state.temp = temp
    st.session_state.rain = rain
    st.session_state.nitro = nitro

# ---------------- OUTPUT ----------------
with col2:
    st.header("🔮 Yield Prediction")

    if st.button("🚀 Predict Yield"):
        yield_value = (rain * 0.01) + (nitro * 0.05) - abs(25 - temp) * 0.2
        yield_value = max(yield_value, 0)

        result = f"Estimated crop yield is {yield_value:.2f} tons per hectare."

        if yield_value < 12:
            advice = "Not suitable for planting. Improve irrigation or soil nutrients."
        else:
            advice = "Suitable for planting. Conditions are favorable."

        st.success(result)
        st.info(advice)

        # 🔊 ONE SINGLE AUDIO OUTPUT
        speak(result + " " + advice)

# ---------------- FOOTER ----------------
st.divider()
st.caption("AgriVision AV — Voice-driven agricultural intelligence 🌾")
