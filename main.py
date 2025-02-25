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
        model="gpt-4o-mini",    #"gpt-4-1106-preview",      # gpt-4
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

<definitions id="definitions"
             xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL"
             xmlns:flowable="http://flowable.org/bpmn"
             targetNamespace="Examples" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xsi:schemaLocation="
             http://www.omg.org/spec/BPMN/20100524/MODEL http://www.omg.org/spec/BPMN/2.0/20100501/BPMN20.xsd">


    <process id="camelProcess">

        <startEvent id="start"/>
        <sequenceFlow id="flow1" sourceRef="start" targetRef="serviceTask1"/>

        <serviceTask id="serviceTask1" flowable:type="camel"/>
        <sequenceFlow id="flow2" sourceRef="serviceTask1" targetRef="receive"/>

        <receiveTask id="receive" name="Wait State" />

        <sequenceFlow id="flow3" sourceRef="receive" targetRef="serviceTask2"/>

        <serviceTask id="serviceTask2" flowable:type="camel"/>

        <sequenceFlow id="flow4" sourceRef="serviceTask2" targetRef="end"/>
        <endEvent id="end"/>

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
                if file_content != None:
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
    
