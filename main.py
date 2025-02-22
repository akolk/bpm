import streamlit as st
import openai
import speech_recognition as sr
import os
from pydub import AudioSegment
from pydub.playback import play

from streamlit_webrtc import webrtc_streamer
import speech_recognition as sr
import openai  # If using OpenAI's GPT model for chatbot

def transcribe_audio(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)
    
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Could not understand the audio."
    except sr.RequestError:
        return "Error in request to speech recognition API."

# Function to recognize speech from audio
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Spreek...")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)  # Google Speech API
            return text
        except sr.UnknownValueError:
            return "Sorry, I kan dat niet verstaan of begrijpen."
        except sr.RequestError:
            return "Speech Recognition service is niet beschikbaar."

client = openai.OpenAI()

def generate_bpmn(text):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Create a BPMN XML for the following process: {text}"}]
    )
    return response.choices[0].message.content

st.title("BPM Generator Chatbot")
st.write("Speak, upload an audio file, or type a process description to generate a BPMN file.")

input_type = st.radio("Choose Input Type:", ("Text", "Speech", "Audio File"))

if input_type == "Text":
    user_input = st.text_area("Enter process description:")
    if st.button("Generate BPMN"):
        if user_input:
            bpmn_output = generate_bpmn(user_input)
            st.download_button("Download BPMN", bpmn_output, "process.bpmn", "text/xml")
        else:
            st.warning("Please enter a process description.")

elif input_type == "Speech":

    audio_value = st.audio_input("Vertel het over het proces.")

    if audio_value:
       transcript = client.audio.transcriptions.create(
          model="whisper-1",
          file = audio_value
       )

    transcript_text = transcript.text
    st.write(transcript_text)
    
    #st.write("Click the button and speak your process description.")
    #text = recognize_speech()
    #if text:
    #    bpmn_output = generate_bpmn(text)
    #    st.download_button("Download BPMN file", bpmn_output, "process.bpmn", "text/xml")

elif input_type == "Audio File":
    uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "m4a"])
    if uploaded_file:
        file_path = f"temp.{uploaded_file.name.split('.')[-1]}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
        text = transcribe_audio(file_path)
        st.write(f"Recognized text: {text}")
        if text:
            bpmn_output = generate_bpmn(text)
            st.download_button("Download BPMN", bpmn_output, "process.bpmn", "text/xml")
