import streamlit as st
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import os
import base64

# --- Setup ---
translator = Translator()
recognizer = sr.Recognizer()

# Function to turn text into speech and play it in Streamlit
def speak(text, lang='hi'):
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save("response.mp3")
    
    # Read the audio file and encode it to play in the browser
    with open("response.mp3", "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

# --- UI ---
st.title("🌱 AgriVision (AV)")

languages = {"Hindi": "hi", "Telugu": "te", "Tamil": "ta", "English": "en"}
sel_lang = st.sidebar.selectbox("Bhasha / Language", list(languages.keys()))
code = languages[sel_lang]

# 1. Voice Input Section
st.subheader("🎤 Speak to AV")
if st.button("Tap to Speak / बोलने के लिए दबाएं"):
    with sr.Microphone() as source:
        st.info("Listening... बोलिए...")
        audio = recognizer.listen(source)
        try:
            # Recognizes the farmer's native language
            user_text = recognizer.recognize_google(audio, language=code)
            st.success(f"You said: {user_text}")
            
            # 2. Logic & Response
            # For the hackathon, we'll simulate a simple prediction
            prediction_text = "आपका अनुमानित उत्पादन 15 टन है" if code == 'hi' else "Your predicted yield is 15 tons."
            
            st.write(f"**AV Says:** {prediction_text}")
            speak(prediction_text, lang=code) # AV speaks back!
            
        except Exception as e:
            st.error("Could not hear clearly. please try again.")

# 3. Simple Visuals
st.progress(70)
st.write("Soil Health: 70% Good")