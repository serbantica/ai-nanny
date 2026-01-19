import streamlit as st

def render_device_card(device):
    """
    Renders a card view for a device.
    """
    st.markdown(f"""
    <div class="device-card">
        <h3>{device['name']}</h3>
        <p>Status: {device['status']}</p>
        <p>Persona: {device.get('active_persona', 'None')}</p>
    </div>
    """, unsafe_allow_html=True)
