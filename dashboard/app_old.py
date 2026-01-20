"""
AI Companion Demo Dashboard - Main Entry Point
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="AI Companion Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple landing page
st.markdown("""
# 🤖 AI Companion Platform

### Welcome to the AI Nanny Dashboard

This is a comprehensive monitoring and control platform for AI companion devices in elderly care facilities.

## 📋 Quick Navigation

Use the sidebar menu to access:

- **🎯 DASHBOARD** - System overview and real-time monitoring
- **📱 DEVICES** - Manage and monitor connected devices
- **🎭 PERSONAS** - Configure AI personas and personalities  
- **🎮 SIMULATOR** - Test conversations and interactions
- **📊 ANALYTICS** - View usage statistics and insights
- **📚 KNOWLEDGE** - Manage knowledge base documents
- **🔍 RAG SYSTEM** - Search and test retrieval system
- **🧠 REAL DEVICE** - Virtual device interface

---

### 🚀 Getting Started

1. Check the **DASHBOARD** page for system status
2. View registered **DEVICES** across facilities
3. Activate a **PERSONA** on a device
4. Test interactions in the **SIMULATOR**

### 📊 System Status

""")

# Quick API status check
try:
    import httpx
    response = httpx.get("http://localhost:8000/health", timeout=2.0)
    if response.status_code == 200:
        st.success("✅ Backend API is connected and running")
    else:
        st.warning("⚠️ Backend API returned unexpected status")
except:
    st.error("❌ Backend API is not available. Please start the orchestrator service.")

st.markdown("""
---
*Use the sidebar menu on the left to navigate to different sections.*
""")
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
