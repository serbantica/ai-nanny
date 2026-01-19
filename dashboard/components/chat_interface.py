import streamlit as st

def render_chat_interface(messages):
    """
    Renders the chat history.
    """
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
