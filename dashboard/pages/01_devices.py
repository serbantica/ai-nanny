"""
Device Management Page
"""

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Devices", page_icon="📱", layout="wide")

st.title("📱 Device Management")

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["Device List", "Register Device", "Device Groups"])


def get_devices(status, device_type, group):
    """Fetch devices from API with filters."""
    # Mock data for now
    return [
        {"id": "dev_001", "name": "living-room-companion", "status": "online",
         "active_persona": "companion", "location": "Living Room", "last_heartbeat": "2 min ago"},
        {"id": "dev_002", "name": "bedroom-assistant", "status": "offline",
         "active_persona": None, "location": "Bedroom", "last_heartbeat": "3 hours ago"}
    ]


def register_device(name, device_type, location, group, capabilities):
    return {"device_id": f"dev_{name.replace('-', '_')}", "auth_token": "mock_token_" + name}


def get_device_groups():
    return [{"id": "grp_001", "name": "Facility A", "description": "Main facility",
             "devices": [{"name": "Room 101", "status": "online"}]}]


with tab1:
    st.subheader("Registered Devices")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Status", ["All", "Online", "Offline", "Busy"])
    with col2:
        type_filter = st.selectbox("Device Type", ["All", "Raspberry Pi", "Smart Speaker", "Tablet"])
    with col3:
        group_filter = st.selectbox("Group", ["All", "Facility A", "Facility B", "Test Lab"])
    
    # Device table
    devices = get_devices(status_filter, type_filter, group_filter)
    
    if devices:
        for device in devices:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 2, 1])
                
                with col1:
                    st.markdown(f"**{device['name']}**")
                    st.caption(f"ID: {device['id']}")
                
                with col2:
                    status_class = "status-online" if device['status'] == 'online' else "status-offline"
                    st.markdown(f"<span class='{status_class}'>{device['status'].upper()}</span>", 
                              unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"🎭 {device['active_persona'] or 'None'}")
                
                with col4:
                    st.markdown(f"📍 {device['location']}")
                    st.caption(f"Last seen: {device['last_heartbeat']}")
                
                with col5:
                    if st.button("Manage", key=f"manage_{device['id']}"):
                        st.session_state['selected_device'] = device['id']
                        st.rerun()
                
                st.divider()

with tab2:
    st.subheader("Register New Device")
    
    with st.form("register_device_form"):
        name = st.text_input("Device Name", placeholder="living-room-companion")
        device_type = st.selectbox("Device Type", ["raspberry_pi", "smart_speaker", "tablet", "custom"])
        location = st.text_input("Location", placeholder="Living Room")
        group = st.selectbox("Device Group", ["None", "Facility A", "Facility B"])
        
        capabilities = st.multiselect(
            "Capabilities",
            ["audio_input", "audio_output", "buttons", "leds", "display"],
            default=["audio_input", "audio_output"]
        )
        
        submitted = st.form_submit_button("Register Device")
        
        if submitted and name:
            result = register_device(name, device_type, location, group, capabilities)
            if result:
                st.success(f"Device registered! ID: {result['device_id']}")
                st.code(f"Auth Token: {result['auth_token']}")

with tab3:
    st.subheader("Device Groups")
    groups = get_device_groups()
    
    for group in groups:
        with st.expander(f"📁 {group['name']} ({len(group['devices'])} devices)"):
            st.markdown(group['description'])
            for device in group['devices']:
                st.markdown(f"- {device['name']} ({device['status']})")
