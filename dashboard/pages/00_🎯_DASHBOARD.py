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


# --- Helper Functions ---

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
    try:
        import httpx
        res = httpx.get("http://localhost:8000/api/v1/devices", timeout=2.0)
        if res.status_code == 200:
            devices = res.json()
            return len(devices)
    except:
        pass
    return 0


def get_active_sessions():
    """Get count of active sessions (Devices with active persona)."""
    try:
        import httpx
        res = httpx.get("http://localhost:8000/api/v1/devices", timeout=2.0)
        if res.status_code == 200:
            devices = res.json()
            return sum(1 for d in devices if d.get('active_persona'))
    except:
        pass
    return 0


def get_live_activities():
    """Fetch real-time device status as activity items."""
    activities = []
    try:
        import httpx
        res = httpx.get("http://localhost:8000/api/v1/devices", timeout=2.0)
        if res.status_code == 200:
            devices = res.json()
            for d in devices:
                status_text = "Online - Standing By"
                if d.get('status') == 'offline':
                    status_text = "Offline - Connection Lost"
                elif d.get('active_persona'):
                    status_text = f"Active Session: {d['active_persona']}"
                elif d.get('status') == 'busy':
                    status_text = "Processing Request"
                
                activities.append({
                    "device": d.get('name'),
                    "location": d.get('location', 'Unknown'),
                    "status": status_text,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
    except:
        pass
    return activities


def get_admin_activities():
    """Get persistent admin activity log from API."""
    try:
        import httpx
        res = httpx.get("http://localhost:8000/api/v1/admin/activity")
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return []


def main():
    # Sidebar
    with st.sidebar:
        # st.image("logo.png", width=200) # TODO: Add logo.png
        st.title("🎯 DASHBOARD")
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
    st.title("🎯 AI COMPANION DASHBOARD")
    st.markdown("### Real-time Monitoring & Control Center")
    
    # Overview cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        with st.container():
            st.subheader("📱 Devices")
            st.write("Manage registered devices")
            if st.button("Go to Devices", use_container_width=True):
                st.switch_page("pages/01_DEVICES.py")
    
    with col2:
        with st.container():
            st.subheader("🎭 Personas")
            st.write("Browse persona library")
            if st.button("Go to Personas", use_container_width=True):
                st.switch_page("pages/02_PERSONAS.py")
    
    with col3:
        with st.container():
            st.subheader("💬 Simulator")
            st.write("Test device interactions")
            if st.button("Go to Simulator", use_container_width=True):
                st.switch_page("pages/03_SIMULATOR.py")
    
    with col4:
        with st.container():
            st.subheader("📊 Analytics")
            st.write("View usage metrics")
            if st.button("Go to Analytics", use_container_width=True):
                st.switch_page("pages/04_ANALYTICS.py")

    with col5:
        with st.container():
            st.subheader("🧠 Knowledge")
            st.write("Train/Update Content")
            if st.button("Go to Knowledge", use_container_width=True):
                st.switch_page("pages/05_KNOWLEDGE.py")
    
    # Recent activity
    st.markdown("---")
    st.subheader("Activity Feed")
    
    tab_monitoring, tab_admin = st.tabs(["👁️ Environment Monitoring", "🛠️ Admin Activity"])
    
    with tab_monitoring:
        st.info("Live status from connected environments")
        live_activities = get_live_activities()
        if live_activities:
            for activity in live_activities:
                # Color code based on status
                icon = "🟢" if "Active" in activity['status'] else "✅" if "Online" in activity['status'] else "🔴"
                with st.container():
                     col_icon, col_details, col_time = st.columns([0.5, 4, 1.5])
                     col_icon.markdown(f"### {icon}")
                     col_details.markdown(f"**{activity['device']}** ({activity['location']})")
                     col_details.caption(f"{activity['status']}")
                     col_time.caption(datetime.now().strftime("%H:%M:%S")) # Mock real-time
                     st.divider()
        else:
            st.warning("No devices detected.")

    with tab_admin:
        st.info("Recent configuration changes and imports")
        admin_activities = get_admin_activities()
        for activity in admin_activities:
             with st.container():
                col_type, col_desc, col_date = st.columns([1, 3, 1])
                col_type.markdown(f"**{activity['type']}**")
                col_desc.text(activity['description'])
                col_date.caption(activity['timestamp'])
                st.divider()


if __name__ == "__main__":
    main()
