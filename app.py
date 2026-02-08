import streamlit as st
import re
import pandas as pd
from gtts import gTTS
from deep_translator import GoogleTranslator
import uuid, base64, os

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
if "data" not in st.session_state:
    st.session_state.data = []

# ---------------- UTILS ----------------
def extract_value(text, keys, default):
    for k in keys:
        m = re.search(rf"{k}[^0-9]*([0-9]+)", text.lower())
        if m:
            return int(m.group(1))
    return default

def speak(text, lang):
    file = f"{uuid.uuid4()}.mp3"
    gTTS(text=text, lang=lang).save(file)
    audio = open(file, "rb").read()
    b64 = base64.b64encode(audio).decode()
    st.markdown(
        f"<audio autoplay><source src='data:audio/mp3;base64,{b64}'></audio>",
        unsafe_allow_html=True
    )
    os.remove(file)

def translate(text, lang):
    return GoogleTranslator(source="auto", target=lang).translate(text)

# ---------------- HEADER ----------------
st.title("🌱 AgriVision (AV)")
st.caption("Speech → Stored Data → Auto Prediction")

# ---------------- LANGUAGE ----------------
lang_map = {"English":"en","Hindi":"hi","Tamil":"ta","Telugu":"te","Marathi":"mr"}
lang = st.sidebar.selectbox("Language", list(lang_map.keys()))
lang_code = lang_map[lang]

# ---------------- SPEECH INPUT ----------------
st.subheader("🎤 Speak your farm details")

speech_js = """
<script>
const r = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
r.lang = 'en-US';
function start() { r.start(); }
r.onresult = e => {
document.getElementById("speech").value = e.results[0][0].transcript;
};
</script>

<textarea id="speech" rows="2" style="width:100%"
placeholder="temperature 30 rainfall 1200 nitrogen 60"></textarea>
<br><button onclick="start()">🎙️ Speak</button>
"""
st.components.v1.html(speech_js, height=160)

spoken = st.text_input("Detected Speech")

# ---------------- SAVE BUTTON (KEY FIX) ----------------
if st.button("💾 Save Speech Data"):
    t = extract_value(spoken, ["temperature","temp"], st.session_state.temp)
    r = extract_value(spoken, ["rainfall","rain"], st.session_state.rain)
    n = extract_value(spoken, ["nitrogen","nitro"], st.session_state.nitro)

    st.session_state.data.append({
        "Temperature": t,
        "Rainfall": r,
        "Nitrogen": n
    })

    st.session_state.temp = t
    st.session_state.rain = r
    st.session_state.nitro = n

    st.success("Speech data stored successfully ✅")

# ---------------- DATA TABLE ----------------
st.subheader("📋 Stored Speech Data")
df = pd.DataFrame(st.session_state.data)
st.dataframe(df, use_container_width=True)

st.divider()
c1, c2 = st.columns(2)

# ---------------- INPUT ----------------
with c1:
    temp = st.slider("🌡 Temperature (°C)", 10, 50, st.session_state.temp)
    rain = st.slider("🌧 Rainfall (mm)", 200, 3000, st.session_state.rain)
    nitro = st.number_input("🧪 Nitrogen", 0, 150, st.session_state.nitro)

# ---------------- OUTPUT ----------------
with c2:
    if st.button("🚀 Predict"):
        yield_val = (rain*0.01) + (nitro*0.05) - abs(25-temp)*0.2
        result = f"Estimated crop yield is {yield_val:.2f} tons per hectare."

        advice = (
            "Suitable for planting. Conditions are favorable."
            if yield_val >= 12 else
            "Not suitable for planting. Improve irrigation or nutrients."
        )

        st.success(translate(result, lang_code))
        st.info(translate(advice, lang_code))

        speak(translate(f"{result} {advice}", lang_code), lang_code)

st.caption("AgriVision AV — robust speech-driven farming intelligence 🌾")
