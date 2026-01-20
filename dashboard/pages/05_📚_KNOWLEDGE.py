"""
Knowledge Base & RAG Management
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Add parent dir to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.api_client import APIClient

st.set_page_config(page_title="Knowledge Base", page_icon="🧠", layout="wide")

st.title("🧠 Knowledge Base Management")
st.markdown("Import documents and update Persona instructions.")

client = APIClient()

# Layout
col_upload, col_train = st.columns([2, 1])

with col_upload:
    st.subheader("Import Knowledge")
    
    # Context Selector
    personas = []
    try:
        import httpx
        res = httpx.get(f"{client.base_url}/personas")
        if res.status_code == 200:
            personas = [p['id'] for p in res.json()]
    except:
        pass
    
    context_options = ["Global (All Personas)"] + personas
    selected_context = st.selectbox("Assign to Context", context_options)
    
    persona_id = None if selected_context == "Global (All Personas)" else selected_context

    # Document Category
    category_options = [
        "Behavioral Guidelines",  # Updates persona instructions/personality
        "Facility Protocols",     # Safety/Emergency rules
        "Domain Knowledge",       # Stories, Medical Info, Trivia
        "Conversation Examples"   # Few-shot training data
    ]
    selected_category = st.selectbox("Document Category", category_options)
    
    # File Uploader
    uploaded_file = st.file_uploader("Upload Instructions/Protocol (PDF, TXT, MD)", type=['txt', 'md', 'pdf'])
    
    if uploaded_file and st.button("Ingest Document"):
        with st.spinner("Processing document..."):
            try:
                # In a real app we'd use client.ingest_document(file, persona_id)
                # Here we use httpx directly for multipart upload simulation
                import httpx
                
                # Streamlit file buffer needs to be passed correctly
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                data = {"category": selected_category}
                if persona_id:
                    data["persona_id"] = persona_id
                
                res = httpx.post(f"{client.base_url}/knowledge/ingest", files=files, data=data) 
                
                if res.status_code == 200:
                    doc = res.json()
                    st.success(f"Ingested {doc['filename']} (Chunks: {doc['chunk_count']})")
                    
                    # Update Recent Imports (client refresh)
                    st.success("Log updated.")
                    
                else:
                    st.error(f"Ingestion failed: {res.text}")
                    
            except Exception as e:
                st.error(f"Error: {e}")

with col_train:
    st.subheader("Model Updates")
    st.info("When new documents are added, the retrieval index may need updating.")
    
    if st.button("Update Knowledge Index"):
        with st.spinner("Re-indexing..."):
            try:
                import httpx
                res = httpx.post(f"{client.base_url}/knowledge/train", params={"persona_id": persona_id} if persona_id else {})
                if res.status_code == 200:
                    st.success("Index Updated Successfully")
                else:
                    st.error("Update failed")
            except Exception as e:
                st.error(f"Error: {e}")

st.divider()

st.subheader("Recent Imports")
# Fetch from API
try:
    import httpx
    hist_res = httpx.get(f"{client.base_url}/knowledge/history")
    if hist_res.status_code == 200:
        history = hist_res.json()
        # Transform for display
        df_data = [{
            "Filename": h['filename'],
            "Context": h.get('context', 'Global'),
            "Category": h.get('category', 'General'),
            "Date": h.get('upload_date', '-'),
            "Status": h['status']
        } for h in history]
        st.dataframe(df_data)
    else:
        st.warning("Could not fetch history.")
except Exception as e:
    st.error(f"Connection error: {e}")
