import streamlit as st
import plotly.express as px

def render_metrics_chart(data, x, y, title):
    """
    Renders a standard metrics chart.
    """
    st.subheader(title)
    fig = px.line(data, x=x, y=y, template='plotly_white')
    st.plotly_chart(fig, use_container_width=True)
