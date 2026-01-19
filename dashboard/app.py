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
        # st.image("logo.png", width=200) # TODO: Add logo.png
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
