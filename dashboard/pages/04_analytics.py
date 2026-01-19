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
