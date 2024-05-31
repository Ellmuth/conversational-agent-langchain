import streamlit as st
import requests
import json

def fetch_sessions():
    response = requests.get("http://localhost:8000/sessions/")
    return response.json().get("sessions", [])

def fetch_knowledge(session_id):
    response = requests.get(f"http://localhost:8000/knowledge/{session_id}")
    return response.json().get("knowledge", [])

st.title("AI Chat Application")

# Sidebar for session management
st.sidebar.title("Sessions")
session_list = fetch_sessions()
selected_session = st.sidebar.selectbox("Select Session", options=["New Session"] + session_list)

if selected_session == "New Session":
    if st.sidebar.button("Start New Chat"):
        response = requests.post("http://localhost:8000/new_chat/")
        new_session_id = response.json().get("session_id")
        st.session_state.session_id = new_session_id
        st.session_state.knowledge = []
else:
    st.session_state.session_id = selected_session
    st.session_state.knowledge = fetch_knowledge(selected_session)

session_id = st.session_state.get("session_id", "")
knowledge = st.session_state.get("knowledge", [])
user_message = st.text_input("Your Message:")

if st.button("Send"):
    url = f"http://localhost:8000/chat/"
    message_payload = {"user_message": user_message, "session_id": session_id}

    with st.spinner("Waiting for response..."):
        response = requests.post(url, json=message_payload, stream=True)

        for chunk in response.iter_lines():
            if chunk:
                result = json.loads(chunk.decode('utf-8'))
                st.write("AI Response:", result.get("ai_response"))

    st.text_input("Session ID", value=session_id, key="session_id_display", disabled=True)

st.sidebar.title("Knowledge Base")
for knowledge_item in knowledge:
    st.sidebar.write(knowledge_item)
