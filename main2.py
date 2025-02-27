import streamlit as st
import json
import logging
import speech_recognition as sr
import openai

logging.basicConfig(level=logging.INFO)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="https://unpkg.com/bpmn-js@18.3.1/dist/assets/bpmn-js.css">
    <script src="https://unpkg.com/bpmn-js@18.3.1/dist/bpmn-modeler.development.js"></script>
    <style>
        #canvas { width: 100%; height: 100vh; border: 1px solid #ccc; }
    </style>
</head>
<body>
<div id="canvas"></div>
<script>
    var viewer = new BpmnJS({ container: '#canvas' });
    async function renderBPMN(xml) {
        try {
            await viewer.importXML(xml);
        } catch (err) {
            console.error('Could not render BPMN', err);
        }
    }
    window.renderBPMN = renderBPMN;
</script>
</body>
</html>
"""

client = openai.OpenAI()

def generate_bpmn(description):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "user", "content": f"Maak een BPMN notatie van het volgende proces: {description}"},
            {"role": "user", "content": "Geef een JSON object terug met de velden: diagram.bpmn, annotatie.md, proces_beschrijving.md"}
        ]
    )
    return json.loads(response.choices[0].message.content)


def render_bpmn_diagram(bpmn_xml):
    html_code = HTML_TEMPLATE + f"<script>renderBPMN(`{bpmn_xml}`);</script>"
    st.components.v1.html(html_code, height=550)


def handle_text_input():
    user_input = st.text_area("Geef een beschrijving van het proces:")
    if st.button("Generate BPMN") and user_input:
        files = generate_bpmn(user_input)
        display_files(files)


def handle_voice_input():
    audio_value = st.audio_input("Vertel het proces en klik op stop wanneer klaar.")
    if audio_value:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_value)
        st.write(transcript.text)
        files = generate_bpmn(transcript.text)
        display_files(files)


def display_files(files):
    for file_name, file_content in files.items():
        if file_name == "diagram.bpmn":
            render_bpmn_diagram(file_content)
        if file_content:
            st.download_button(file_name, file_content, file_name, "text/xml")


st.title("BPM Generator Chatbot")
st.write("Geef een proces beschrijving via tekst of spraak om een BPMN diagram te genereren.")

input_type = st.radio("Kies invoer type", ("Text", "Spraak"))

if input_type == "Text":
    handle_text_input()
elif input_type == "Spraak":
    handle_voice_input()
