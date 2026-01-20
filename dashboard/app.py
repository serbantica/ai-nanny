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
