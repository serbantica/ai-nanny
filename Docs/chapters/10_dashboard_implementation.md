## 10. Dashboard Implementation - Full Implementation

### 10.1 Overview

The demo dashboard is built with Streamlit for rapid prototyping and stakeholder demos. It provides:
- Device management and monitoring
- Persona library browsing
- Live device simulator (chat interface)
- Analytics and metrics

### 10.2 Application Structure

```
dashboard/
├── app.py                      # Main entry point
├── pages/
│   ├── 01_devices.py          # Device management
│   ├── 02_personas.py         # Persona library
│   ├── 03_simulator.py        # Device simulator
│   └── 04_analytics.py        # Usage analytics
├── components/
│   ├── device_card.py         # Reusable device card
│   ├── persona_selector.py    # Persona dropdown
│   ├── chat_interface.py      # Chat UI component
│   └── metrics_display.py     # Metrics charts
├── services/
│   └── api_client.py          # Backend API client
├── requirements.txt
└── .streamlit/
    └── config.toml            # Streamlit configuration
```

### 10.3 Main Application Entry Point

```python
# dashboard/app.py
"""
AI Companion Demo Dashboard - Main Entry Point
"""

import streamlit as st
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Companion Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #f5f7fa;
    }
    .device-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .status-online {
        color: #28a745;
        font-weight: bold;
    }
    .status-offline {
        color: #dc3545;
        font-weight: bold;
    }
    .persona-tag {
        background: #e9ecef;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Sidebar
    with st.sidebar:
        st.image("logo.png", width=200)
        st.title("AI Companion")
        st.markdown("---")
        
        # Connection status
        api_status = check_api_status()
        if api_status:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Disconnected")
        
        st.markdown("---")
        
        # Quick stats
        st.subheader("Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Devices", get_device_count())
        with col2:
            st.metric("Sessions", get_active_sessions())
    
    # Main content
    st.title("🤖 AI Companion Platform")
    st.markdown("### Welcome to the AI Companion Demo Dashboard")
    
    # Overview cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="device-card">
            <h3>📱 Devices</h3>
            <p>Manage registered devices</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="device-card">
            <h3>🎭 Personas</h3>
            <p>Browse persona library</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="device-card">
            <h3>💬 Simulator</h3>
            <p>Test device interactions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="device-card">
            <h3>📊 Analytics</h3>
            <p>View usage metrics</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent activity
    st.markdown("---")
    st.subheader("Recent Activity")
    
    activities = get_recent_activities()
    for activity in activities:
        with st.expander(f"{activity['timestamp']} - {activity['type']}", expanded=False):
            st.json(activity['details'])


def check_api_status():
    """Check if backend API is reachable."""
    try:
        import httpx
        response = httpx.get("http://localhost:8000/health", timeout=2.0)
        return response.status_code == 200
    except:
        return False


def get_device_count():
    """Get count of registered devices."""
    return st.session_state.get('device_count', 0)


def get_active_sessions():
    """Get count of active sessions."""
    return st.session_state.get('session_count', 0)


def get_recent_activities():
    """Get recent platform activities."""
    return st.session_state.get('activities', [])


if __name__ == "__main__":
    main()
```

### 10.4 Device Management Page

```python
# dashboard/pages/01_devices.py
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


def get_devices(status, device_type, group):
    """Fetch devices from API with filters."""
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
```

### 10.5 Device Simulator Page

```python
# dashboard/pages/03_simulator.py
"""
Device Simulator - Test device interactions
"""

import streamlit as st
from datetime import datetime
import time

st.set_page_config(page_title="Simulator", page_icon="💬", layout="wide")

st.title("💬 Device Simulator")

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
```

### 10.6 Analytics Page

```python
# dashboard/pages/04_analytics.py
"""
Analytics Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")

st.title("📊 Platform Analytics")

# Key metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Interactions", "12,847", delta="+15%")
with col2:
    st.metric("Active Devices", "42", delta="+3")
with col3:
    st.metric("Avg Response Time", "1.2s", delta="-0.3s", delta_color="inverse")
with col4:
    st.metric("User Satisfaction", "4.6/5", delta="+0.2")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Interactions Over Time")
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    interactions = [100 + i * 10 + (i % 7) * 20 for i in range(30)]
    df = pd.DataFrame({'Date': dates, 'Interactions': interactions})
    fig = px.line(df, x='Date', y='Interactions', template='plotly_white')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Persona Distribution")
    persona_data = pd.DataFrame({
        'Persona': ['Companion', 'Medication Nurse', 'Storyteller', 'Entertainer', 'Emergency'],
        'Usage': [45, 25, 15, 12, 3]
    })
    fig = px.pie(persona_data, values='Usage', names='Persona', hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
```

### 10.7 Configuration & Requirements

```toml
# dashboard/.streamlit/config.toml
[theme]
primaryColor = "#4CAF50"
backgroundColor = "#f5f7fa"
secondaryBackgroundColor = "#ffffff"

[server]
headless = true
port = 8501
```

```
# dashboard/requirements.txt
streamlit>=1.31.0
pandas>=2.0.0
plotly>=5.18.0
httpx>=0.26.0
```

### 10.8 Running the Dashboard

```bash
cd dashboard
streamlit run app.py
```

---
