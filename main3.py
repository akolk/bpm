import streamlit as st
import openai
import html 

client = openai.OpenAI()
# Streamlit Page Configuration
st.set_page_config(layout="wide")

# Sidebar for File Upload
st.sidebar.title("Upload File")
uploaded_file = st.sidebar.file_uploader("Choose a file", type=["bpmn", "txt", "doc"])
if filename.lower().endswith(".bpmn"):
    st.session_state.file_type = "bpmn" 

if uploaded_file:
    file_content = uploaded_file.read().decode("utf-8")
    #if 'file_content' not in st.session_state:
   st.session_state.file_content = file_content
   st.session_state.file_type = "bpmn" 

# Chat Interface
st.title("Chat with your BPMN File using GPT-4o")
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("BPMN Modeller View")
    if uploaded_file:
        modeller_code = f"""
                    {html.html_code}
                    <script>
                    renderBPMN(`{st.session_state.file_content}`);
                    </script>
                    </body>
                    </html>
                    """
        st.components.v1.html(modeller_code, height=400)
    else:
        st.info("Upload a BPMN file to start.")

with col2:
    st.subheader("Chat Interface")
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Type your message here...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # OpenAI API Call
        #openai.api_key = os.getenv("OPENAI_KEY")
        messages_payload = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]
        messages_payload.insert(0, {"role": "system", "content": f"File Content: {st.session_state.file_content}"})

        response = client.chat.completions.create(
               model="gpt-4o-mini",    #"gpt-4-1106-preview",      # gpt-4
               response_format= { "type": "json_object" },
               messages=[{"role": "user", "content": 
                   f"""
                   Je bent een BPMN specialist en je antwoord alleen in een JSON object.
                   Maak een BPMN notatie en een BPMN 2.0 XML-formaat van het volgende proces: {prompt}
                   """},
                  {"role": "user", "content": 
                   """
                   Geef een JSON object terug met de volgende velden:
                   {
                     "diagram.bpmn": "De diagram in Blue Dolphin compatible XML.",
                     "annotatie.md": "De BPMN annotatie van het process in markdown formaat.",
                     "proces_beschrijving.md": "De formele beschrijving van het proces in markdown formaat.",
                     "bot_reply": "Wat heb je gedaan"
                   }
                   """}
                 ]
        )
        
        #response = openai.ChatCompletion.create(
        #    model="gpt-4o-mini",
        #    messages=messages_payload
        #)

        bot_reply = response.choices[0].message["content"]
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.markdown(bot_reply)
