import streamlit as st

def render_persona_selector(personas, key="persona_selector"):
    """
    Renders a dropdown to select a persona.
    """
    return st.selectbox("Select Persona", [p['name'] for p in personas], key=key)
