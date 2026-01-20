"""
Persona Management Page
"""

import streamlit as st

st.set_page_config(page_title="Personas", page_icon="🎭", layout="wide")

st.title("🎭 Persona Library")

def get_personas():
    """Fetch personas (mock data)."""
    return [
        {
            "id": "companion",
            "name": "General Companion",
            "description": "A friendly, conversational companion for daily chats.",
            "voice": "Rachel",
            "tone": "Warm and empathetic"
        },
        {
            "id": "medication_nurse",
            "name": "Medication Nurse",
            "description": "Reminds users to take medication and tracks compliance.",
            "voice": "Emily",
            "tone": "Professional and caring"
        },
        {
            "id": "storyteller",
            "name": "Storyteller",
            "description": "Reads audiobooks and tells interactive stories.",
            "voice": "Josh",
            "tone": "Engaging and dramatic"
        },
        {
            "id": "entertainer",
            "name": "Entertainer",
            "description": "Plays music, quizzes, and games.",
            "voice": "Sam",
            "tone": "Upbeat and fun"
        },
        {
            "id": "emergency",
            "name": "Emergency Responder",
            "description": "Handles emergencies and contacts family/authorities.",
            "voice": "Alice",
            "tone": "Calm and authoritative"
        }
    ]

personas = get_personas()

# Display personas in a grid
cols = st.columns(3)

for idx, persona in enumerate(personas):
    with cols[idx % 3]:
        with st.container():
            st.markdown(f"""
            <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h3>{persona['name']}</h3>
                <p><strong>ID:</strong> {persona['id']}</p>
                <p>{persona['description']}</p>
                <p><strong>Voice:</strong> {persona['voice']}</p>
                <p><strong>Tone:</strong> {persona['tone']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Edit {persona['name']}", key=persona['id']):
                st.info(f"Edit functionality for {persona['name']} coming soon.")

st.markdown("### Create New Persona")
with st.expander("Create a new persona"):
    with st.form("new_persona"):
        st.text_input("Name")
        st.text_area("Description")
        st.text_area("System Prompt")
        st.selectbox("Voice", ["Rachel", "Emily", "Josh", "Sam", "Alice"])
        st.form_submit_button("Create Persona")
