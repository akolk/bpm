import streamlit as st
import openai

# Streamlit Page Configuration
st.set_page_config(layout="wide")

# Sidebar for File Upload
st.sidebar.title("Upload File")
uploaded_file = st.sidebar.file_uploader("Choose a file", type=["bpmn"])

if uploaded_file:
    file_content = uploaded_file.read().decode("utf-8")
    if 'file_content' not in st.session_state:
        st.session_state.file_content = file_content

# Chat Interface
st.title("Chat with your BPMN File using GPT-4o")
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("BPMN Modeller View")
    if uploaded_file:
        st.components.v1.html(f"<pre>{st.session_state.file_content}</pre>", height=400)
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
        
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages_payload
        )

        bot_reply = response.choices[0].message["content"]
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.markdown(bot_reply)
