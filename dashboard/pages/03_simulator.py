"""
Device Simulator - Test device interactions
"""

import streamlit as st
from datetime import datetime
import time

st.set_page_config(page_title="Simulator", page_icon="💬", layout="wide")

st.title("💬 Device Simulator")

def simulate_response(prompt: str, persona: str) -> dict:
    time.sleep(0.5)
    responses = {
        "companion": "That's interesting! Tell me more about that.",
        "medication_nurse": "I understand. Have you taken your afternoon pills?",
        "storyteller": "Once upon a time, in a land far away...",
        "entertainer": "Great question! How about we play a trivia game?",
        "emergency": "I'm here with you. Can you tell me what's happening?"
    }
    return {"text": responses.get(persona, "I'm here to help!"), "latency_ms": 1200}

# Sidebar for device/persona selection
with st.sidebar:
    st.subheader("Configuration")
    device = st.selectbox("Select Device", ["dev_001 (Living Room)", "dev_002 (Bedroom)", "virtual_device"])
    persona = st.selectbox("Active Persona", ["companion", "medication_nurse", "storyteller", "entertainer", "emergency"])
    
    if st.button("Switch Persona"):
        with st.spinner("Switching persona..."):
            time.sleep(1)
            st.session_state['current_persona'] = persona
            st.success(f"Switched to {persona}")

# Initialize chat history
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'current_persona' not in st.session_state:
    st.session_state.current_persona = "companion"

# Chat interface
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("### Conversation")
    
    for message in st.session_state.chat_messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(message["content"])
                st.caption(f"Persona: {message.get('persona', 'unknown')} | Latency: {message.get('latency_ms', 0)}ms")
    
    if prompt := st.chat_input("Type your message..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt, "timestamp": datetime.now().isoformat()})
        
        with st.spinner("Thinking..."):
            response = simulate_response(prompt, st.session_state.current_persona)
        
        st.session_state.chat_messages.append({
            "role": "assistant", "content": response["text"],
            "persona": st.session_state.current_persona, "latency_ms": response["latency_ms"]
        })
        st.rerun()

with col2:
    st.markdown("### Device State")
    st.metric("Status", "🟢 Online")
    st.metric("Persona", st.session_state.current_persona)
    st.metric("Messages", len(st.session_state.chat_messages))
    
    st.divider()
    st.markdown("**Physical Buttons**")
    
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        if st.button("🔴", help="Emergency"):
            st.session_state.current_persona = "emergency"
            st.rerun()
    with col_btn2:
        if st.button("🟢", help="Companion"):
            st.session_state.current_persona = "companion"
            st.rerun()
    with col_btn3:
        if st.button("🔵", help="Activity"):
            st.session_state.current_persona = "entertainer"
            st.rerun()
