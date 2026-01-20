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
    # Show last 24 hours with hourly data
    hours = pd.date_range(end=datetime.now(), periods=24, freq='h')
    # Generate realistic hourly interaction data with smoother variations
    # Peak during daytime (8am-8pm), lower at night, small random variations
    import math
    interactions = []
    for i in range(24):
        hour = (datetime.now() - timedelta(hours=23-i)).hour
        # Base activity: higher during day (8-20), lower at night
        if 8 <= hour <= 20:
            base = 45  # Daytime baseline
        else:
            base = 20  # Nighttime baseline
        # Add small natural variation (±15%)
        variation = math.sin(i * 0.5) * 5 + (i % 2) * 3
        interactions.append(int(base + variation))
    
    df = pd.DataFrame({'Time': hours, 'Interactions': interactions})
    fig = px.line(df, x='Time', y='Interactions', template='plotly_white')
    fig.update_xaxes(title_text="Time (Last 24 Hours)", tickformat='%H:%M')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Persona Distribution")
    persona_data = pd.DataFrame({
        'Persona': ['Companion', 'Medication Nurse', 'Storyteller', 'Entertainer', 'Emergency'],
        'Usage': [45, 25, 15, 12, 3]
    })
    fig = px.pie(persona_data, values='Usage', names='Persona', hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
