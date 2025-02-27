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
    <!--<script src="https://unpkg.com/bpmn-js/dist/bpmn-viewer.development.js"></script> -->
        <!-- required modeler styles -->
    <link rel="stylesheet" href="https://unpkg.com/bpmn-js@18.3.1/dist/assets/bpmn-js.css">
    <link rel="stylesheet" href="https://unpkg.com/bpmn-js@18.3.1/dist/assets/diagram-js.css">
    <link rel="stylesheet" href="https://unpkg.com/bpmn-js@18.3.1/dist/assets/bpmn-font/css/bpmn.css">

    <!-- modeler distro -->
    <script src="https://unpkg.com/bpmn-js@18.3.1/dist/bpmn-modeler.development.js"></script>
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
        var viewer = new BpmnJS({ container: '#canvas' });  
        
        async function renderBPMN(xml) {
            await viewer.importXML(xml) 
        }
        window.renderBPMN = renderBPMN;
    </script>

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

#st.components.v1.html(html_code)

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
    #logging.info(response)
    #logging.info(response.choices[0].message.content)
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
            #print(files)
           
            #st.download_button("Download BPMN", bpmn_output, "process.bpmn", "text/xml")

            for file_name, file_content in files.items():
                if file_name == "diagram.bpmn":
                    dia_code = f"""
                    {html_code}
                    <script>
                    renderBPMN(`{file_content}`);
                    </script>
                    </body>
                    </html>
                    """
                    st.components.v1.html(dia_code, height=550)        
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
       if "downloaded_transcript" not in st.session_state:
           st.session_state.downloaded_transcript = False

       # Download button
       if st.download_button(label="Download Transcription", file_name="transcription.txt",data=transcript_text,):
          st.session_state.downloaded_transcript = True

       files = generate_bpmn(st, transcript.text)
       for file_name, file_content in files.items():
           if file_name == "diagram.bpmn":
                    dia_code = f"""
                    {html_code}
                    <script>
                    renderBPMN(`{file_content}`);
                    </script>
                    </body>
                    </html>
                    """
                    st.components.v1.html(dia_code, height=550)        
           if file_content != None:
                    st.download_button(file_name, file_content, file_name, "text/xml")
       # Show success message after download
       if st.session_state.downloaded_transcript:
          st.success("Transcription file downloaded successfully!")
    
