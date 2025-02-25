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
        model="gpt-4o-mini"    #"gpt-4-1106-preview",      # gpt-4
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
<bpmn2:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:bpmn2="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:camunda="http://camunda.org/schema/1.0/bpmn" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" xsi:schemaLocation="http://www.omg.org/spec/BPMN/20100524/MODEL BPMN20.xsd" id="_ll67ABGYEeW7xqkBzIjHqw" exporter="camunda modeler" exporterVersion="2.7.0" targetNamespace="http://camunda.org/schema/1.0/bpmn">
  <bpmn2:process id="Sample" name="Sample" isExecutable="true" camunda:historyTimeToLive="P180D">
    <bpmn2:startEvent id="StartEvent_1">
      <bpmn2:outgoing>SequenceFlow_1</bpmn2:outgoing>
    </bpmn2:startEvent>
    <bpmn2:userTask id="UserTask_1" name="do something">
      <bpmn2:incoming>SequenceFlow_1</bpmn2:incoming>
      <bpmn2:outgoing>SequenceFlow_2</bpmn2:outgoing>
    </bpmn2:userTask>
    <bpmn2:sequenceFlow id="SequenceFlow_1" sourceRef="StartEvent_1" targetRef="UserTask_1"/>
    <bpmn2:serviceTask id="ServiceTask_1" camunda:delegateExpression="${sayHelloDelegate}" camunda:async="true" name="say hello">
      <bpmn2:incoming>SequenceFlow_2</bpmn2:incoming>
      <bpmn2:outgoing>SequenceFlow_3</bpmn2:outgoing>
    </bpmn2:serviceTask>
    <bpmn2:sequenceFlow id="SequenceFlow_2" sourceRef="UserTask_1" targetRef="ServiceTask_1"/>
    <bpmn2:endEvent id="EndEvent_1">
      <bpmn2:incoming>SequenceFlow_3</bpmn2:incoming>
    </bpmn2:endEvent>
    <bpmn2:sequenceFlow id="SequenceFlow_3" name="" sourceRef="ServiceTask_1" targetRef="EndEvent_1"/>
  </bpmn2:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Sample">
      <bpmndi:BPMNShape id="_BPMNShape_StartEvent_3" bpmnElement="StartEvent_1">
        <dc:Bounds height="36.0" width="36.0" x="65.0" y="97.0"/>
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="_BPMNShape_UserTask_3" bpmnElement="UserTask_1">
        <dc:Bounds height="80.0" width="100.0" x="151.0" y="75.0"/>
      </bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="BPMNEdge_SequenceFlow_1" bpmnElement="SequenceFlow_1" sourceElement="_BPMNShape_StartEvent_3" targetElement="_BPMNShape_UserTask_3">
        <di:waypoint xsi:type="dc:Point" x="101.0" y="115.0"/>
        <di:waypoint xsi:type="dc:Point" x="151.0" y="115.0"/>
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNShape id="_BPMNShape_ServiceTask_2" bpmnElement="ServiceTask_1">
        <dc:Bounds height="80.0" width="100.0" x="301.0" y="75.0"/>
      </bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="BPMNEdge_SequenceFlow_2" bpmnElement="SequenceFlow_2" sourceElement="_BPMNShape_UserTask_3" targetElement="_BPMNShape_ServiceTask_2">
        <di:waypoint xsi:type="dc:Point" x="251.0" y="115.0"/>
        <di:waypoint xsi:type="dc:Point" x="301.0" y="115.0"/>
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNShape id="_BPMNShape_EndEvent_3" bpmnElement="EndEvent_1">
        <dc:Bounds height="36.0" width="36.0" x="451.0" y="97.0"/>
      </bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="BPMNEdge_SequenceFlow_3" bpmnElement="SequenceFlow_3" sourceElement="_BPMNShape_ServiceTask_2" targetElement="_BPMNShape_EndEvent_3">
        <di:waypoint xsi:type="dc:Point" x="401.0" y="115.0"/>
        <di:waypoint xsi:type="dc:Point" x="451.0" y="115.0"/>
      </bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn2:definitions>
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
    
