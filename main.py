import streamlit as st
import openai
import speech_recognition as sr
import os
import json
import logging

from pydub import AudioSegment
from pydub.playback import play

from streamlit_webrtc import webrtc_streamer
import speech_recognition as sr
import openai  # If using OpenAI's GPT model for chatbot


logging.basicConfig(level=logging.INFO)
html_code = """
<head>
    <script src="https://unpkg.com/bpmn-js@10.0.0/dist/bpmn-viewer.production.min.js"></script>
</head>
<body>
    <div id="bpmn-container" style="width: 100%; height: 500px; border: 1px solid #ccc;"></div>
    <script>
        const viewer = new BpmnJS({ container: "#bpmn-container" });        
    </script>
</body>
"""

#fetch("https://cdn.jsdelivr.net/gh/bpmn-io/bpmn-js-examples@master/starter/diagram.bpmn")
#            .then(response => response.text())
#            .then(diagramXML => viewer.importXML(diagramXML))
#            .catch(err => console.log(err));

st.components.v1.html(html_code, height=550)

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

def generate_bpmn(st, text):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": 
                   f"Maak een BPMN notatie en een BPMN diagram voor een process. {text}"},
                  {"role": "user", "content": """
Geef een JSON structuur terug met de volgende velden:
{
    "diagram.xml": "De visualisatie van het process in XML.",
    "annotatie.md": "De BPMN annotatie van het process.",
    "proces_beschrijving.md": "De formele beschrijving van het proces."
}
"""}
                 ]
    )
    logging.info(response)
    logging.info(response.choices[0].message.content)
    files_data = response.choices[0].message.content
    #files_data = json.loads(response["choices"][0]["message"]["content"])
    #logging.info(files_data)
    return files_data

        
st.title("BPM Generator Chatbot")
st.write("Geef een proces beschrijving (spreek die in of type die in) en de BPMN bestanden worden gemaakt.")

input_type = st.radio("Kies invoer type ", ("Text", "Spraak"))

if input_type == "Text":
    user_input = st.text_area("Geef een beschrijving van het proces: ")
    if st.button("Generate BPMN"):
        if user_input:
            files = generate_bpmn(st, user_input)
            print(files)
            test="""
            <?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL"
             xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
             xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
             xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
             targetNamespace="http://bpmn.io/schema/bpmn">

  <process id="OpvoerenNieuweKlant" name="Opvoeren Nieuwe Klant" isExecutable="true">
    
    <!-- Start Event -->
    <startEvent id="StartEvent" name="Nieuwe klantaanvraag ontvangen"/>
    
    <!-- Stap 1: Aanvraag indienen -->
    <task id="AanvraagIndienen" name="Verkoper dient klantgegevens in"/>
    <sequenceFlow sourceRef="StartEvent" targetRef="AanvraagIndienen"/>
    
    <!-- Stap 2: KYC-controle -->
    <task id="KYCControle" name="Compliance controleert klant (KYC)"/>
    <sequenceFlow sourceRef="AanvraagIndienen" targetRef="KYCControle"/>
    
    <!-- Gateway: KYC goedgekeurd? -->
    <exclusiveGateway id="KYC_Gateway" name="KYC goedgekeurd?"/>
    <sequenceFlow sourceRef="KYCControle" targetRef="KYC_Gateway"/>
    
    <!-- KYC Afwijzing -->
    <endEvent id="AfwijzingKYC" name="Klant afgewezen"/>
    <sequenceFlow sourceRef="KYC_Gateway" targetRef="AfwijzingKYC">
      <conditionExpression xsi:type="tFormalExpression">false</conditionExpression>
    </sequenceFlow>
    
    <!-- Stap 3: Kredietwaardigheidscontrole -->
    <task id="KredietControle" name="Financiële controle (kredietwaardigheid)"/>
    <sequenceFlow sourceRef="KYC_Gateway" targetRef="KredietControle">
      <conditionExpression xsi:type="tFormalExpression">true</conditionExpression>
    </sequenceFlow>
    
    <!-- Gateway: Krediet goedgekeurd? -->
    <exclusiveGateway id="Krediet_Gateway" name="Krediet goedgekeurd?"/>
    <sequenceFlow sourceRef="KredietControle" targetRef="Krediet_Gateway"/>
    
    <!-- Krediet Afwijzing -->
    <endEvent id="AfwijzingKrediet" name="Klant afgewezen"/>
    <sequenceFlow sourceRef="Krediet_Gateway" targetRef="AfwijzingKrediet">
      <conditionExpression xsi:type="tFormalExpression">false</conditionExpression>
    </sequenceFlow>
    
    <!-- Stap 4: Klantregistratie in systeem -->
    <task id="Registratie" name="IT registreert klant in CRM/ERP"/>
    <sequenceFlow sourceRef="Krediet_Gateway" targetRef="Registratie">
      <conditionExpression xsi:type="tFormalExpression">true</conditionExpression>
    </sequenceFlow>
    
    <!-- Stap 5: Bevestiging versturen -->
    <task id="Bevestiging" name="Bevestiging naar klant en verkoopteam"/>
    <sequenceFlow sourceRef="Registratie" targetRef="Bevestiging"/>
    
    <!-- End Event -->
    <endEvent id="Einde" name="Klant succesvol geregistreerd"/>
    <sequenceFlow sourceRef="Bevestiging" targetRef="Einde"/>
    
  </process>
</definitions>
"""
            #st.download_button("Download BPMN", bpmn_output, "process.bpmn", "text/xml")
            dia_code = f"""
            <script>
                viewer.importXML({test});
            </script>
            """
            st.components.v1.html(dia_code, height=550)
            for file_name, file_content in files.items():
                st.download_button(file_name, bpmn_output, file_name, "text/xml")
            #components.html(dia_code, height=550)
        else:
            st.warning("Geef een beschrijving van het proces.")

elif input_type == "Spraak":

    audio_value = st.audio_input("Vertel het over het proces.")

    if audio_value:
       
       transcript = client.audio.transcriptions.create(
          model="whisper-1",
          file = audio_value
       )

       transcript_text = transcript.text
       #st.write(transcript_text)
       txt_file = "transcription.txt"

       # Initialize session state for download confirmation
       if "downloaded" not in st.session_state:
           st.session_state.downloaded = False

       # Download button
       if st.download_button(
          label="Download Transcription",
          file_name="transcription.txt",data=transcript_text,
          ):
          st.session_state.downloaded = True


       output = generate_bpmn(st, transcript.text)
       # Show success message after download
       if st.session_state.downloaded:
          st.success("Transcription file downloaded successfully!")
    
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
