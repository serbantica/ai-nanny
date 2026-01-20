"""
Device Simulator - Test device interactions
"""

import streamlit as st
from datetime import datetime
import time
import sys
import os

# Add parent dir to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.api_client import APIClient

st.set_page_config(page_title="Simulator", page_icon="💬", layout="wide")

st.title("💬 Device Simulator")

# Initialize API Client
client = APIClient()

# Initialize Session State
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'current_persona' not in st.session_state:
    st.session_state.current_persona = "companion"

# Sidebar for device configuration
with st.sidebar:
    st.subheader("Device Configuration")
    
    # Fetch registered devices
    try:
        import httpx
        response = httpx.get(f"{client.base_url}/devices")
        devices_list = response.json() if response.status_code == 200 else []
    except:
        devices_list = []
    
    # Select Device Logic
    if devices_list:
        device_options = {d['name']: d['id'] for d in devices_list}
        selected_device_name = st.selectbox("Select Registered Device", list(device_options.keys()))
        device_id = device_options[selected_device_name]
        st.caption(f"ID: {device_id}")
    else:
        # Fallback to manual entry
        device_id_input = st.text_input("Device ID (Manual)", value="dev_001")
        device_id = device_id_input
    
    st.subheader("Persona Control")
    # Fetch personas from backend
    known_personas = ["companion", "medication_nurse", "storyteller", "entertainer", "emergency"]
    persona_selection = st.selectbox("Select Persona", known_personas)
    
    if st.button("Activate Persona"):
        with st.spinner(f"Activating {persona_selection}..."):
            try:
                client.activate_persona(device_id, persona_selection)
                st.session_state.current_persona = persona_selection
                st.success(f"Active: {persona_selection}")
                # Add system message
                st.session_state.chat_messages.append({
                    "role": "system",
                    "content": f"System: Switched to {persona_selection} persona."
                })
            except Exception as e:
                st.error(f"Failed: {str(e)}")

    st.divider()
    
    st.subheader("Multi-Device Actions")
    st.markdown("**Group Activity**")
    
    target_ids = []
    if devices_list:
        other_options = {d['name']: d['id'] for d in devices_list if d['id'] != device_id}
        if other_options:
            selected_participants = st.multiselect("Other Participants", list(other_options.keys()))
            target_ids = [other_options[name] for name in selected_participants]
        else:
            st.info("No other devices registered.")
    else:
        target_str = st.text_input("Target Devices (comma sep)", value="dev_002")
        target_ids = [x.strip() for x in target_str.split(",") if x.strip()]

    activity_type = st.selectbox("Activity", ["trivia", "story", "sing_along"])
    
    if st.button("Start Group Activity"):
        full_participants = list(target_ids)
        # Add current device if not in list
        if device_id not in full_participants:
            full_participants.append(device_id)
            
        try:
            res = client.start_group_activity(activity_type, full_participants, st.session_state.current_persona)
            st.success(f"Started Activity: {res.get('id')}")
            st.session_state.chat_messages.append({
                "role": "system", 
                "content": f"📣 GROUP ACTIVITY STARTED: {activity_type}"
            })
        except Exception as e:
            st.error(f"Error: {str(e)}")

    st.markdown("**Session Handoff**")
    
    handoff_target = None
    if devices_list:
        other_options = {d['name']: d['id'] for d in devices_list if d['id'] != device_id}
        if other_options:
            handoff_name = st.selectbox("Handoff To", list(other_options.keys()))
            handoff_target = other_options[handoff_name]
        else:
            st.info("No other devices available.")
    else:
        handoff_target = st.text_input("Handoff To (Device ID)", value="dev_002")

    if st.button("Initiate Handoff"):
        if handoff_target:
            try:
                # Mock session ID for demo
                mock_session = "sess_" + str(int(time.time()))
                client.initiate_handoff(mock_session, device_id, handoff_target)
                st.info(f"Handoff sent to {handoff_target}")
            except Exception as e:
                st.error(f"Handoff failed: {str(e)}")
        else:
            st.warning("Please select a target device.")

# Chat interface
st.subheader(f"Device: {device_id} | Persona: {st.session_state.current_persona}")

# Display chat history
for message in st.session_state.chat_messages:
    role = message["role"]
    if role == "system":
        st.info(message["content"])
    else:
        with st.chat_message(role):
            st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Type a message..."):
    # Add user message
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Simulate response (in a real app, this would call the /chat endpoint)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            time.sleep(1) # Mock latency
            response_text = f"[{st.session_state.current_persona}] I heard you say: '{prompt}'. (Backend connection active)"
            st.markdown(response_text)
            st.session_state.chat_messages.append({"role": "assistant", "content": response_text})

