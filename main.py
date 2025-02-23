import streamlit as st
import os
import json
import logging

from streamlit_webrtc import webrtc_streamer
import speech_recognition as sr
import openai  # If using OpenAI's GPT model for chatbot

logging.basicConfig(level=logging.INFO)

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://unpkg.com/bpmn-js@18.3.1/dist/bpmn-navigated-viewer.development.js"></script>
    <style>
        html, body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            width: 100%;
            height: 100%;
        }
        #canvas {
            width: 100%;
            height: 100vh;
            border: 1px solid #ccc;
        }
    </style>
</head>
<body>
    <div id="canvas"></div>
    <script>
        function renderBPMN(xml) {
            var viewer = new BpmnJS({ container: '#canvas' });
            viewer.importXML(xml, function(err) {
                if (err) {
                    console.error("Could not import BPMN diagram:", err);
                }
            });
        }
        window.renderBPMN = renderBPMN;
    </script>
</body>
</html>
"""

#<body>
#    <div id="bpmn-container" style="width: 100%; height: 500px; border: 1px solid #ccc;"></div>
#    <script>
#        const viewer = new BpmnJS({ container: "#bpmn-container" });        
#    </script>
#</body>

#fetch("https://cdn.jsdelivr.net/gh/bpmn-io/bpmn-js-examples@master/starter/diagram.bpmn")
#            .then(response => response.text())
#            .then(diagramXML => viewer.importXML(diagramXML))
#            .catch(err => console.log(err));

st.components.v1.html(html_code)

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
        model="gpt-4-1106-preview",      # gpt-4
        response_format= { "type": "json_object" },
        messages=[{"role": "user", "content": 
                   f"""
                   Je bent een BPMN specialist en je antwoord alleen in een JSON object.
                   Maak een BPMN notatie en een BPMN 2.0 XML-formaat van het volgende proces: {text}
                   """},
                  {"role": "user", "content": 
                   """
                   Geef een JSON object terug met de volgende velden:
                   {
                     "diagram.bpmn": "De diagram in Blue Dolphin compatible XML.",
                     "annotatie.md": "De BPMN annotatie van het process in markdown formaat.",
                     "proces_beschrijving.md": "De formele beschrijving van het proces in markdown formaat."
                   }
                   """}
                 ]
    )
    logging.info(response)
    logging.info(response.choices[0].message.content)
    files_data = json.loads(response.choices[0].message.content)
    #files_data = json.loads(response["choices"][0]["message"]["content"])
    logging.info(files_data)
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
            {html_code}
            <script>
              setTimeout(function() {{
                 renderBPMN(`{test}`);
              }}, 500);
            </script>
            """
            st.components.v1.html(dia_code, height=550)
            for file_name, file_content in files.items():
                st.download_button(file_name, file_content, file_name, "text/xml")
            #st.components.v1.html(dia_code, height=550)
        else:
            st.warning("Geef een beschrijving van het proces.")

elif input_type == "Spraak":

    audio_value = st.audio_input("Klik op de microfoon en wacht een paar seconden. Vertel dan het over het proces. Klik op stop wanneer je klaar bent")

    if audio_value:

       st.write("Bezig met transcriptie ...")
       transcript = client.audio.transcriptions.create(
          model="whisper-1",
          file = audio_value
       )

       transcript_text = transcript.text
       st.write(transcript_text)
       txt_file = "transcription.txt"

       # Initialize session state for download confirmation
       if "downloaded" not in st.session_state:
           st.session_state.downloaded = False

       # Download button
       if st.download_button(label="Download Transcription", file_name="transcription.txt",data=transcript_text,):
          st.session_state.downloaded = True


       output = generate_bpmn(st, transcript.text)
       # Show success message after download
       if st.session_state.downloaded:
          st.success("Transcription file downloaded successfully!")
    
