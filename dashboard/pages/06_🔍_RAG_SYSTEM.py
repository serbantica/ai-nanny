"""
RAG (Retrieval-Augmented Generation) Dashboard
Comprehensive interface for RAG system management and exploration
"""

import streamlit as st
import sys
import os
import httpx
import json
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Add parent dir to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.api_client import APIClient

st.set_page_config(
    page_title="RAG System", 
    page_icon="🧬", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧬 RAG System Dashboard")
st.markdown("**Retrieval-Augmented Generation** • Semantic Search • Knowledge Management")

# Important notice about lazy loading
st.info("""
    ⚡ **Performance Mode**: This page uses lazy loading to avoid unnecessary API calls.
    - Configuration and data are loaded only when you click the relevant buttons
    - The RAG engine initializes only when you perform actions (search, load metrics, etc.)
    - This keeps the dashboard fast and responsive
""")

client = APIClient()

# Initialize session state for config
if 'rag_config_loaded' not in st.session_state:
    st.session_state.rag_config_loaded = False
    st.session_state.current_config = {
        "chunk_size": 500,
        "chunk_overlap": 50,
        "embedding_model": "text-embedding-3-small",
        "embedding_dimension": 1536,
        "top_k": 5,
        "score_threshold": 0.7,
        "similarity_metric": "cosine",
        "vector_store_path": "data/vector_store"
    }

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ RAG Configuration")
    
    # Load config button
    if st.button("🔄 Load Current Config", help="Fetch configuration from API"):
        try:
            config_response = httpx.get(f"{client.base_url}/knowledge/config", timeout=10.0)
            if config_response.status_code == 200:
                st.session_state.current_config = config_response.json()
                st.session_state.rag_config_loaded = True
                st.success("✅ Configuration loaded!")
            else:
                st.error("Failed to load config")
        except Exception as e:
            st.error(f"Cannot connect to API: {e}")
    
    if st.session_state.rag_config_loaded:
        st.caption("✅ Config loaded from API")
    else:
        st.caption("⚠️ Using default values (click Load Config)")
    
    st.divider()
    
    st.subheader("Chunking Parameters")
    chunk_size = st.slider(
        "Chunk Size (chars)", 
        100, 2000, 
        st.session_state.current_config.get("chunk_size", 500),
        help="Size of text chunks for embedding"
    )
    chunk_overlap = st.slider(
        "Chunk Overlap (chars)", 
        0, 500, 
        st.session_state.current_config.get("chunk_overlap", 50),
        help="Overlap between consecutive chunks"
    )
    
    st.subheader("Embedding Settings")
    
    # Embedding provider selection
    embedding_provider = st.radio(
        "Embedding Provider",
        ["sentence-transformers", "openai"],
        index=0 if st.session_state.current_config.get("embedding_provider", "sentence-transformers") == "sentence-transformers" else 1,
        help="Choose between local (free) or OpenAI (paid) embeddings"
    )
    
    # Model selection based on provider
    if embedding_provider == "sentence-transformers":
        st.success("✅ Using local embeddings (no API costs!)")
        sentence_models = [
            "all-MiniLM-L6-v2",  # Fast, 384 dim
            "all-mpnet-base-v2",  # Better quality, 768 dim
            "paraphrase-multilingual-MiniLM-L12-v2"  # Multilingual
        ]
        embedding_model = st.selectbox(
            "Sentence-Transformer Model",
            sentence_models,
            index=0,
            help="all-MiniLM-L6-v2: Fast & efficient (384 dims)\nall-mpnet-base-v2: Higher quality (768 dims)"
        )
        embedding_dimension = 384 if "MiniLM" in embedding_model else 768
        st.caption(f"📐 Embedding dimensions: {embedding_dimension}")
        
    else:  # openai
        st.warning("⚠️ OpenAI API key required")
        openai_models = [
            "text-embedding-3-small",
            "text-embedding-3-large",
            "text-embedding-ada-002"
        ]
        embedding_model = st.selectbox(
            "OpenAI Embedding Model",
            openai_models,
            index=0,
            help="text-embedding-3-small: Fast, cost-effective\ntext-embedding-3-large: Higher quality"
        )
        embedding_dimension = 1536 if "small" in embedding_model or "ada" in embedding_model else 3072
        st.caption(f"📐 Embedding dimensions: {embedding_dimension}")
    
    st.subheader("Search Parameters")
    top_k = st.slider(
        "Top K Results", 
        1, 20, 
        st.session_state.current_config.get("top_k", 5),
        help="Number of results to return"
    )
    score_threshold = st.slider(
        "Score Threshold", 
        0.0, 1.0, 
        st.session_state.current_config.get("score_threshold", 0.7),
        0.05,
        help="Minimum similarity score"
    )
    
    similarity_metric = st.selectbox(
        "Similarity Metric",
        ["cosine", "euclidean", "dot"],
        index=0
    )
    
    st.info(f"💾 Vector Store: `{st.session_state.current_config.get('vector_store_path', 'data/vector_store')}`")

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📖 Setup Guide",
    "🔍 Semantic Search", 
    "📊 System Metrics", 
    "📚 Knowledge Base", 
    "⚡ Quick Test"
])

# ===== TAB 0: SETUP GUIDE =====
with tab1:
    st.header("📖 RAG System Setup & Configuration Guide")
    
    # Introduction
    st.markdown("""
    ### What is RAG?
    
    **RAG (Retrieval-Augmented Generation)** is a powerful AI technique that combines:
    - **Document Storage**: Upload and organize knowledge documents
    - **Semantic Understanding**: AI embeddings that understand meaning, not just keywords
    - **Smart Retrieval**: Find relevant information based on context and intent
    - **Enhanced Responses**: Provide AI companions with factual, up-to-date information
    
    Think of RAG as a smart library system where AI companions can quickly find and reference 
    the exact information they need to provide accurate, helpful responses to residents.
    """)
    
    st.divider()
    
    # Parameter Guide
    st.subheader("🎛️ Parameter Configuration Guide")
    
    param_col1, param_col2 = st.columns(2)
    
    with param_col1:
        st.markdown("#### 📐 Chunking Parameters")
        
        with st.expander("**Chunk Size** - How to Set", expanded=True):
            st.markdown("""
            **What it does:** Determines how large each text segment is (in characters)
            
            **How to set:**
            - **Short Documents (FAQs, Q&A):** 200-400 characters
            - **Standard Documents (Protocols):** 400-600 characters  
            - **Long Narratives (Stories, Guides):** 800-1200 characters
            
            **Current Setting:** Use the slider in the sidebar →
            
            **Tips:**
            - Larger chunks = More context but less precise
            - Smaller chunks = More precise but may miss context
            - Test with your content type
            
            **Example:**
            ```
            chunk_size=500 means each piece contains 
            approximately 2-3 paragraphs of text
            ```
            """)
        
        with st.expander("**Chunk Overlap** - How to Set"):
            st.markdown("""
            **What it does:** How much text overlaps between consecutive chunks
            
            **How to set:**
            - **Recommended:** 10-20% of chunk_size
            - **Low Overlap (20-40):** Faster, uses less storage
            - **Medium Overlap (50-100):** Balanced, preserves context
            - **High Overlap (100-200):** Best context, more storage
            
            **Current Setting:** Use the slider in the sidebar →
            
            **Why it matters:**
            Prevents information from being "split" awkwardly at chunk boundaries
            
            **Example:**
            ```
            chunk_size=500, overlap=50
            Chunk 1: chars 0-500
            Chunk 2: chars 450-950 (overlaps by 50)
            ```
            """)
    
    with param_col2:
        st.markdown("#### 🎯 Embedding Parameters")
        
        with st.expander("**Embedding Provider** - How to Choose", expanded=True):
            st.markdown("""
            **What it does:** The system that converts text into numerical vectors (embeddings)
            
            **Options:**
            
            **1. sentence-transformers (LOCAL - Recommended)** ✅
            - **100% Free** - No API costs
            - **Private** - All processing on your machine
            - **Fast** - No network latency
            - **No API Key needed**
            - Models:
              - `all-MiniLM-L6-v2`: Fast, efficient (384 dims)
              - `all-mpnet-base-v2`: Higher quality (768 dims)
            
            **2. openai (CLOUD)** 
            - **Paid API** - Usage-based pricing
            - **Requires OpenAI API Key**
            - **Highest Quality** - State-of-the-art embeddings
            - Models:
              - `text-embedding-3-small`: $0.02/1M tokens (1536 dims)
              - `text-embedding-3-large`: $0.13/1M tokens (3072 dims)
            
            **How to set:** Choose provider in sidebar radio button →
            
            **Recommendation:**
            - **Start with sentence-transformers** - Free and works great!
            - **Upgrade to OpenAI** only if you need the absolute best quality
            
            **Performance Comparison:**
            ```
            Local (MiniLM):  90% accuracy, 0ms latency, $0 cost
            Local (mpnet):   93% accuracy, 5ms latency, $0 cost
            OpenAI (small):  95% accuracy, 50ms latency, low cost
            OpenAI (large):  97% accuracy, 60ms latency, higher cost
            ```
            """)
        
        with st.expander("**Embedding Model** - How to Choose"):
            st.markdown("""
            **What it does:** The specific AI model for creating embeddings
            
            **For sentence-transformers (Local):**
            1. **all-MiniLM-L6-v2** (Recommended)
               - Super fast and lightweight
               - 384 dimensions
               - Perfect for most use cases
               - 80MB model size
            
            2. **all-mpnet-base-v2**
               - Higher quality embeddings
               - 768 dimensions
               - Better for complex documents
               - 420MB model size
            
            3. **paraphrase-multilingual-MiniLM-L12-v2**
               - Supports 50+ languages
               - 384 dimensions
               - Use for multilingual content
            
            **For OpenAI (Cloud):**
            1. **text-embedding-3-small** (Recommended)
               - Fast and cost-effective
               - 1536 dimensions
               - $0.02 per 1M tokens
            
            2. **text-embedding-3-large**
               - Highest quality
               - 3072 dimensions
               - $0.13 per 1M tokens
            
            **How to set:** Select from dropdown in sidebar →
            """)
        
        with st.expander("**Embedding Dimension** - Info Only"):
            st.markdown("""
            **What it is:** The size of the vector representation
            
            **You don't need to change this** - it's automatically set based on your chosen model:
            
            **Local models:**
            - all-MiniLM-L6-v2: 384 dims
            - all-mpnet-base-v2: 768 dims
            
            **OpenAI models:**
            - text-embedding-3-small: 1536 dims
            - text-embedding-3-large: 3072 dims
            
            **What it means:**
            Higher dimensions = More detailed understanding but requires more storage
            """)
    
    st.divider()
    
    search_col1, search_col2 = st.columns(2)
    
    with search_col1:
        st.markdown("#### 🔍 Search Parameters")
        
        with st.expander("**Top K** - How Many Results", expanded=True):
            st.markdown("""
            **What it does:** Number of most relevant chunks to return
            
            **How to set:**
            - **Precise Answers (3-5):** When you need specific info
            - **Comprehensive (10-15):** When exploring a topic
            - **Quick Context (1-3):** For fast, focused responses
            
            **Current Setting:** Adjust slider in sidebar →
            
            **Performance Impact:**
            - Lower K = Faster searches
            - Higher K = More context but slower
            
            **Example Use Cases:**
            ```
            "What's the emergency number?" → top_k=1
            "Tell me about fall prevention" → top_k=5
            "Research pain management options" → top_k=15
            ```
            """)
        
        with st.expander("**Score Threshold** - Quality Filter"):
            st.markdown("""
            **What it does:** Minimum relevance score (0.0 to 1.0) to include results
            
            **How to set:**
            - **High Precision (0.8-1.0):** Only very relevant results
            - **Balanced (0.6-0.8):** Good relevance, some flexibility
            - **High Recall (0.4-0.6):** Catch more possibilities
            - **Exploratory (0.3-0.5):** Cast wide net
            
            **Current Setting:** Adjust slider in sidebar →
            
            **Score Meanings:**
            - **0.9-1.0:** Nearly identical content
            - **0.7-0.9:** Good match
            - **0.5-0.7:** Moderate relevance
            - **<0.5:** Weak connection
            
            **Troubleshooting:**
            - No results? Lower threshold to 0.5
            - Too many irrelevant? Raise to 0.8
            """)
    
    with search_col2:
        st.markdown("#### 📊 Advanced Settings")
        
        with st.expander("**Similarity Metric** - How to Choose"):
            st.markdown("""
            **What it does:** Mathematical method to compare vectors
            
            **Options:**
            1. **Cosine (Recommended)**
               - Measures angle between vectors
               - Best for text similarity
               - Scale-independent
            
            2. **Euclidean**
               - Measures absolute distance
               - Sensitive to magnitude
               - Good for spatial data
            
            3. **Dot Product**
               - Fast computation
               - Not normalized
               - Use for performance
            
            **How to set:** Select from dropdown in sidebar →
            
            **When to change:**
            Most cases: Keep as **cosine**
            Special needs: Consult with data team
            """)
        
        with st.expander("**Vector Store Path** - Storage Location"):
            st.markdown("""
            **What it is:** Where embeddings are stored on disk
            
            **Default:** `data/vector_store`
            
            **To change:** Update in `.env` file:
            ```bash
            RAG_VECTOR_STORE_PATH=data/vector_store
            ```
            
            **Storage Size:**
            - 10 docs ≈ 5-15 MB
            - 100 docs ≈ 50-150 MB
            - 1000 docs ≈ 500MB-1.5 GB
            
            **Backup Recommended:**
            Regularly backup this directory to prevent data loss
            """)
    
    st.divider()
    
    # Step-by-Step Setup
    st.subheader("🚀 Step-by-Step Setup Instructions")
    
    setup_tabs = st.tabs(["1️⃣ First Time Setup", "2️⃣ Upload Documents", "3️⃣ Optimize Settings", "4️⃣ Troubleshooting"])
    
    with setup_tabs[0]:
        st.markdown("""
        ### First Time Setup (5 minutes)
        
        #### Prerequisites ✅
        - [ ] API server running on port 8000
        - [ ] OpenAI API key configured in `.env`
        - [ ] Dependencies installed (chromadb, pypdf2)
        
        #### Configuration Steps
        
        **1. Set Environment Variables**
        
        Edit `ai-companion-orchestrator/.env`:
        ```bash
        # Required
        OPENAI_API_KEY=sk-your-key-here
        
        # Optional RAG Settings (these are defaults)
        RAG_CHUNK_SIZE=500
        RAG_CHUNK_OVERLAP=50
        RAG_EMBEDDING_MODEL=text-embedding-3-small
        RAG_TOP_K=5
        RAG_SCORE_THRESHOLD=0.7
        ```
        
        **2. Verify Installation**
        ```bash
        cd ai-companion-orchestrator
        python3 -c "from core.rag import RAGEngine; print('✅ RAG Ready!')"
        ```
        
        **3. Start Services**
        ```bash
        # Terminal 1: API Server
        uvicorn api.main:app --reload --port 8000
        
        # Terminal 2: Dashboard
        cd ../dashboard
        streamlit run app.py
        ```
        
        **4. Check System Status**
        - Go to "System Metrics" tab
        - Click "🔄 Refresh Metrics"
        - Verify "Documents Loaded" shows green 🟢 (after uploading first doc)
        
        **5. Run Quick Test**
        - Go to "Quick Test" tab
        - Click "Test API Connection"
        - All checks should pass ✅
        """)
    
    with setup_tabs[1]:
        st.markdown("""
        ### Upload Your First Documents
        
        #### Document Preparation
        
        **Supported Formats:**
        - `.txt` - Plain text files
        - `.md` - Markdown files
        - `.pdf` - PDF documents
        
        **Best Practices:**
        - ✅ Clean, well-formatted text
        - ✅ Clear headings and structure
        - ✅ 1-50 pages per document
        - ✅ Remove unnecessary headers/footers
        - ❌ Avoid scanned images (no OCR yet)
        - ❌ Don't include sensitive PII without review
        
        #### Upload Process
        
        **Method 1: Via Dashboard**
        1. Go to "Knowledge Base" page (main menu)
        2. Select **context** (Global or specific persona)
        3. Choose **category**:
           - Behavioral Guidelines
           - Facility Protocols
           - Domain Knowledge
           - Conversation Examples
        4. Click "Upload Instructions/Protocol"
        5. Select your file
        6. Click "Ingest Document"
        7. Wait for processing (5-30 seconds)
        
        **Method 2: Via API**
        ```python
        import httpx
        
        files = {"file": open("protocol.pdf", "rb")}
        data = {
            "category": "Facility Protocols",
            "persona_id": "companion_001"  # Optional
        }
        
        response = httpx.post(
            "http://localhost:8000/api/v1/knowledge/ingest",
            files=files,
            data=data
        )
        print(response.json())
        ```
        
        #### Verify Upload
        1. Go to "Knowledge Base" tab on this page
        2. See your document listed
        3. Note the chunk count
        4. Check "System Metrics" for updated counts
        """)
    
    with setup_tabs[2]:
        st.markdown("""
        ### Optimize Your Settings
        
        #### Tuning Process
        
        **1. Establish Baseline**
        - Start with default settings
        - Upload 3-5 test documents
        - Run sample searches
        - Note relevance scores
        
        **2. Adjust Chunking (if needed)**
        
        **Problem:** Search finds right document but wrong section
        **Solution:** Decrease chunk_size to 300-400
        
        **Problem:** Search misses context across sections
        **Solution:** Increase chunk_size to 700-1000 and overlap to 100
        
        **Problem:** Processing is slow
        **Solution:** Increase chunk_size to reduce total chunks
        
        **3. Tune Search Parameters**
        
        **Problem:** No results found
        - Lower score_threshold to 0.5
        - Increase top_k to 10
        - Try different query phrasing
        
        **Problem:** Too many irrelevant results
        - Raise score_threshold to 0.8
        - Decrease top_k to 3
        - Use category filters
        - Make query more specific
        
        **Problem:** Missing important results
        - Increase top_k to 15
        - Lower score_threshold to 0.6
        - Check document was uploaded correctly
        
        **4. Monitor Performance**
        ```
        Go to "Quick Test" tab
        → "Run Performance Test"
        → Check average query time
        
        Target: <200ms per query
        Acceptable: <500ms per query
        Needs optimization: >1000ms
        ```
        
        #### Configuration Presets
        
        **High Precision (Medical/Legal):**
        ```bash
        RAG_CHUNK_SIZE=300
        RAG_CHUNK_OVERLAP=30
        RAG_EMBEDDING_MODEL=text-embedding-3-large
        RAG_SCORE_THRESHOLD=0.85
        RAG_TOP_K=3
        ```
        
        **Balanced (General Purpose):**
        ```bash
        RAG_CHUNK_SIZE=500
        RAG_CHUNK_OVERLAP=50
        RAG_EMBEDDING_MODEL=text-embedding-3-small
        RAG_SCORE_THRESHOLD=0.7
        RAG_TOP_K=5
        ```
        
        **High Recall (Research):**
        ```bash
        RAG_CHUNK_SIZE=800
        RAG_CHUNK_OVERLAP=100
        RAG_EMBEDDING_MODEL=text-embedding-3-small
        RAG_SCORE_THRESHOLD=0.5
        RAG_TOP_K=10
        ```
        """)
    
    with setup_tabs[3]:
        st.markdown("""
        ### Common Issues & Solutions
        
        #### 🔴 "Cannot connect to API"
        **Check:**
        ```bash
        curl http://localhost:8000/health
        ```
        **If fails, restart API:**
        ```bash
        cd ai-companion-orchestrator
        uvicorn api.main:app --reload --port 8000
        ```
        
        #### 🔴 "No results found" (After uploading documents)
        **Steps:**
        1. Check System Metrics → Verify embeddings count > 0
        2. Lower score threshold to 0.5
        3. Try simpler query (single keyword)
        4. Verify document category matches filter
        5. Check query language matches document language
        
        #### 🔴 "OpenAI API Error"
        **Possible causes:**
        - Invalid API key → Check `.env` file
        - Rate limit exceeded → Wait and retry
        - No credits → Check OpenAI account
        - Network issues → Check internet connection
        
        **Debug:**
        ```bash
        echo $OPENAI_API_KEY  # Verify key is set
        curl https://api.openai.com/v1/models \\
          -H "Authorization: Bearer $OPENAI_API_KEY"
        ```
        
        #### 🔴 "ChromaDB initialization failed"
        **Solution:**
        ```bash
        # Reinstall ChromaDB
        pip install --force-reinstall chromadb
        
        # Clear and rebuild
        rm -rf data/vector_store/*
        # Re-upload documents
        ```
        
        #### 🟡 "Slow search performance"
        **Optimizations:**
        - Reduce top_k to 3-5
        - Use category/context filters
        - Switch to text-embedding-3-small
        - Restart API server
        - Check vector store size (<1GB optimal)
        
        #### 🟡 "High API costs"
        **Cost reduction:**
        - Use text-embedding-3-small (13x cheaper)
        - Increase chunk_size (fewer chunks = fewer embeddings)
        - Reduce chunk_overlap
        - Batch document uploads
        - Only embed essential documents
        
        #### 🟡 "Embeddings don't match chunks"
        **Fix:**
        1. Check System Metrics tab
        2. If total_embeddings ≠ total_chunks:
           ```bash
           # Rebuild vector store
           curl -X DELETE http://localhost:8000/api/v1/knowledge/reset
           # Re-upload all documents
           ```
        
        #### Still having issues?
        **Diagnostic steps:**
        1. Go to "Quick Test" tab
        2. Run all system diagnostics
        3. Check terminal logs for errors
        4. Review documentation: `Docs/RAG_IMPLEMENTATION_GUIDE.md`
        5. Contact support with error messages
        """)
    
    st.divider()
    
    # Quick Reference
    st.subheader("📋 Quick Reference Card")
    
    ref_col1, ref_col2, ref_col3 = st.columns(3)
    
    with ref_col1:
        st.markdown("""
        **Chunking**
        - Size: 200-1200 chars
        - Overlap: 10-20% of size
        - Default: 500/50
        """)
    
    with ref_col2:
        st.markdown("""
        **Embedding**
        - Model: 3-small (default)
        - Dimension: Auto-set
        - Cost: $0.02/1M tokens
        """)
    
    with ref_col3:
        st.markdown("""
        **Search**
        - Top K: 3-15 results
        - Threshold: 0.5-0.9
        - Metric: Cosine
        """)
    
    # Tips box
    st.info("""
    💡 **Pro Tips:**
    - Start with defaults, adjust only if needed
    - Test searches after each parameter change
    - Monitor costs in OpenAI dashboard
    - Backup vector_store directory regularly
    - Use category filters to narrow results
    - Document your configuration choices
    """)
    
    st.success("""
    ✅ **Ready to start?** 
    1. Verify settings in sidebar
    2. Go to "Knowledge Base" page to upload documents
    3. Return to "Semantic Search" tab to test queries
    4. Monitor "System Metrics" for health
    """)

# ===== TAB 2: SEMANTIC SEARCH =====
with tab2:
    st.header("Semantic Search Interface")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        query = st.text_area(
            "Enter your search query:",
            placeholder="E.g., 'What are the emergency protocols for falls?' or 'Tell me about medication schedules'",
            height=100
        )
    
    with col2:
        st.markdown("**Search Filters**")
        
        # Load categories/contexts button
        if 'search_filters_loaded' not in st.session_state:
            st.session_state.search_filters_loaded = False
            st.session_state.categories = ["All"]
            st.session_state.contexts = ["All"]
        
        if st.button("📥 Load Filters", help="Load available categories and contexts"):
            try:
                metrics_response = httpx.get(f"{client.base_url}/knowledge/metrics", timeout=10.0)
                if metrics_response.status_code == 200:
                    metrics = metrics_response.json()
                    st.session_state.categories = ["All"] + list(metrics.get("categories", {}).keys())
                    st.session_state.contexts = ["All"] + list(metrics.get("contexts", {}).keys())
                    st.session_state.search_filters_loaded = True
                    st.success("✅ Filters loaded")
                else:
                    st.error("Failed to load filters")
            except:
                st.error("Cannot connect to API")
        
        filter_category = st.selectbox("Category", st.session_state.categories)
        filter_context = st.selectbox("Context/Persona", st.session_state.contexts)
        
        use_custom_params = st.checkbox("Custom search params")
        if use_custom_params:
            custom_top_k = st.number_input("Top K", 1, 50, top_k)
            custom_threshold = st.number_input("Threshold", 0.0, 1.0, score_threshold, 0.05)
        else:
            custom_top_k = top_k
            custom_threshold = score_threshold
    
    if st.button("🔍 Search", type="primary", use_container_width=True):
        if not query:
            st.warning("Please enter a search query")
        else:
            with st.spinner("Searching knowledge base..."):
                try:
                    search_request = {
                        "query": query,
                        "top_k": custom_top_k,
                        "score_threshold": custom_threshold
                    }
                    
                    if filter_category != "All":
                        search_request["category"] = filter_category
                    if filter_context != "All":
                        search_request["context"] = filter_context
                    
                    response = httpx.post(
                        f"{client.base_url}/knowledge/search",
                        json=search_request,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Display search stats
                        col_a, col_b, col_c = st.columns(3)
                        col_a.metric("Results Found", result["count"])
                        col_b.metric("Execution Time", f"{result['execution_time_ms']:.2f} ms")
                        col_c.metric("Query", f"\"{result['query'][:30]}...\"" if len(result['query']) > 30 else f"\"{result['query']}\"")
                        
                        st.divider()
                        
                        # Display results
                        if result["results"]:
                            for idx, res in enumerate(result["results"], 1):
                                with st.expander(f"Result #{idx} - Score: {res['score']:.4f} ({res['metadata'].get('filename', 'Unknown')})", expanded=(idx <= 3)):
                                    # Metadata
                                    meta_cols = st.columns(4)
                                    meta_cols[0].write(f"**Document:** {res['metadata'].get('filename', 'N/A')}")
                                    meta_cols[1].write(f"**Category:** {res['metadata'].get('category', 'N/A')}")
                                    meta_cols[2].write(f"**Context:** {res['metadata'].get('context', 'N/A')}")
                                    meta_cols[3].write(f"**Chunk:** {res['metadata'].get('chunk_index', 'N/A')}")
                                    
                                    st.markdown("---")
                                    st.markdown("**Content:**")
                                    st.markdown(f"```\n{res['content']}\n```")
                                    
                                    # Relevance bar
                                    st.progress(res['score'])
                        else:
                            st.info("No results found. Try adjusting your query or lowering the score threshold.")
                    
                    else:
                        st.error(f"Search failed: {response.text}")
                
                except Exception as e:
                    st.error(f"Search error: {e}")

# ===== TAB 3: SYSTEM METRICS =====
with tab3:
    st.header("RAG System Metrics")
    
    st.info("💡 Click 'Refresh Metrics' to load current system statistics. This will initialize the RAG engine if not already running.")
    
    # Initialize metrics in session state
    if 'metrics_loaded' not in st.session_state:
        st.session_state.metrics_loaded = False
        st.session_state.metrics_data = None
    
    if st.button("🔄 Refresh Metrics", type="primary"):
        with st.spinner("Loading metrics from RAG system..."):
            try:
                metrics_response = httpx.get(f"{client.base_url}/knowledge/metrics", timeout=10.0)
                
                if metrics_response.status_code == 200:
                    st.session_state.metrics_data = metrics_response.json()
                    st.session_state.metrics_loaded = True
                    st.success("✅ Metrics loaded successfully!")
                else:
                    st.error(f"Failed to fetch metrics: {metrics_response.status_code}")
            except Exception as e:
                st.error(f"Error loading metrics: {e}")
    
    if st.session_state.metrics_loaded and st.session_state.metrics_data:
        metrics = st.session_state.metrics_data
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📄 Total Documents", metrics["total_documents"])
        col2.metric("🧩 Total Chunks", metrics["total_chunks"])
        col3.metric("🔢 Total Embeddings", metrics["total_embeddings"])
        col4.metric("💾 Vector Store Size", f"{metrics['vector_store_size_mb']:.2f} MB")
        
        col5, col6, col7 = st.columns(3)
        col5.metric("📏 Avg Chunk Size", f"{metrics['average_chunk_size']} chars")
        col6.metric("🎯 Embedding Dimension", metrics["embedding_dimension"])
        col7.metric("🕐 Last Indexed", metrics.get("last_indexed", "Never")[:10] if metrics.get("last_indexed") else "Never")
        
        st.divider()
        
        # Visualizations
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            st.subheader("Documents by Category")
            if metrics["categories"]:
                cat_df = pd.DataFrame(
                    list(metrics["categories"].items()),
                    columns=["Category", "Count"]
                )
                fig = px.pie(
                    cat_df, 
                    values="Count", 
                    names="Category",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No documents categorized yet")
        
        with viz_col2:
            st.subheader("Documents by Context")
            if metrics["contexts"]:
                ctx_df = pd.DataFrame(
                    list(metrics["contexts"].items()),
                    columns=["Context", "Count"]
                )
                fig = px.bar(
                    ctx_df,
                    x="Context",
                    y="Count",
                    color="Count",
                    color_continuous_scale="Blues"
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No context-specific documents yet")
        
        # System health indicators
        st.subheader("System Health")
        health_col1, health_col2, health_col3 = st.columns(3)
        
        # Calculate health scores
        docs_health = "🟢" if metrics["total_documents"] > 0 else "🔴"
        embeddings_match = metrics["total_embeddings"] == metrics["total_chunks"]
        embeddings_health = "🟢" if embeddings_match else "🟡"
        storage_health = "🟢" if metrics["vector_store_size_mb"] < 1000 else "🟡"
        
        health_col1.markdown(f"**Documents Loaded:** {docs_health}")
        health_col2.markdown(f"**Embeddings Synced:** {embeddings_health}")
        health_col3.markdown(f"**Storage Status:** {storage_health}")
    else:
        st.warning("👆 Click 'Refresh Metrics' to load system statistics")

# ===== TAB 4: KNOWLEDGE BASE BROWSER =====
with tab4:
    st.header("Knowledge Base Browser")
    
    st.info("💡 Click 'Load Documents' to fetch the document list from the knowledge base.")
    
    # Initialize documents in session state
    if 'documents_loaded' not in st.session_state:
        st.session_state.documents_loaded = False
        st.session_state.documents_data = []
    
    if st.button("📥 Load Documents", type="primary"):
        with st.spinner("Loading documents..."):
            try:
                history_response = httpx.get(f"{client.base_url}/knowledge/history", timeout=10.0)
                
                if history_response.status_code == 200:
                    st.session_state.documents_data = history_response.json()
                    st.session_state.documents_loaded = True
                    st.success(f"✅ Loaded {len(st.session_state.documents_data)} documents")
                else:
                    st.error(f"Failed to fetch documents: {history_response.status_code}")
            except Exception as e:
                st.error(f"Error loading documents: {e}")
    
    if st.session_state.documents_loaded:
        documents = st.session_state.documents_data
        
        if documents:
                # Create DataFrame for better display
                df = pd.DataFrame(documents)
                
                # Display summary
                st.markdown(f"**Total Documents:** {len(documents)}")
                
                # Filter controls
                filter_col1, filter_col2 = st.columns(2)
                
                with filter_col1:
                    if "category" in df.columns:
                        selected_categories = st.multiselect(
                            "Filter by Category",
                            options=df["category"].unique(),
                            default=df["category"].unique()
                        )
                    else:
                        selected_categories = []
                
                with filter_col2:
                    if "context" in df.columns:
                        selected_contexts = st.multiselect(
                            "Filter by Context",
                            options=df["context"].unique(),
                            default=df["context"].unique()
                        )
                    else:
                        selected_contexts = []
                
                # Apply filters
                if selected_categories:
                    df = df[df["category"].isin(selected_categories)]
                if selected_contexts:
                    df = df[df["context"].isin(selected_contexts)]
                
                # Display documents
                st.dataframe(
                    df,
                    use_container_width=True,
                    column_config={
                        "id": st.column_config.TextColumn("Document ID", width="small"),
                        "filename": st.column_config.TextColumn("Filename", width="medium"),
                        "chunk_count": st.column_config.NumberColumn("Chunks", width="small"),
                        "category": st.column_config.TextColumn("Category", width="small"),
                        "context": st.column_config.TextColumn("Context", width="small"),
                        "upload_date": st.column_config.TextColumn("Upload Date", width="small"),
                    }
                )
                
                # Document management
                st.subheader("Document Management")
                doc_to_delete = st.selectbox(
                    "Select document to delete",
                    options=[""] + [doc["id"] for doc in documents],
                    format_func=lambda x: f"{x} - {next((d['filename'] for d in documents if d['id'] == x), '')}" if x else "Select..."
                )
                
                if doc_to_delete and st.button("🗑️ Delete Document", type="secondary"):
                    try:
                        delete_response = httpx.delete(
                            f"{client.base_url}/knowledge/documents/{doc_to_delete}",
                            timeout=10.0
                        )
                        if delete_response.status_code == 200:
                            st.success(f"Deleted document: {doc_to_delete}")
                            st.rerun()
                        else:
                            st.error(f"Failed to delete: {delete_response.text}")
                    except Exception as e:
                        st.error(f"Delete error: {e}")
        
        else:
            st.info("📭 No documents in knowledge base. Upload some documents in the Knowledge Base Management page!")
    else:
        st.warning("👆 Click 'Load Documents' to view the knowledge base contents")

# ===== TAB 5: QUICK TEST =====
with tab5:
    st.header("RAG Quick Test Suite")
    st.markdown("Test RAG functionality with sample queries and documents")
    
    test_col1, test_col2 = st.columns(2)
    
    with test_col1:
        st.subheader("🧪 Test Queries")
        
        sample_queries = [
            "What are the emergency protocols?",
            "Tell me about medication management",
            "How to handle a fall incident?",
            "What are the activity recommendations?",
            "Explain the communication guidelines"
        ]
        
        selected_query = st.selectbox("Select a test query", ["Custom..."] + sample_queries)
        
        if selected_query == "Custom...":
            test_query = st.text_input("Enter custom test query")
        else:
            test_query = selected_query
        
        if st.button("🚀 Run Test Search"):
            if test_query:
                with st.spinner("Testing..."):
                    try:
                        response = httpx.post(
                            f"{client.base_url}/knowledge/search",
                            json={"query": test_query, "top_k": 3},
                            timeout=20.0
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ Found {result['count']} results in {result['execution_time_ms']:.2f}ms")
                            
                            if result["results"]:
                                for res in result["results"][:3]:
                                    st.markdown(f"**Score: {res['score']:.3f}** - {res['content'][:200]}...")
                            else:
                                st.warning("No results found. Knowledge base might be empty.")
                        else:
                            st.error(f"Test failed: {response.text}")
                    except Exception as e:
                        st.error(f"Test error: {e}")
    
    with test_col2:
        st.subheader("📈 Performance Benchmarks")
        
        if st.button("Run Performance Test"):
            with st.spinner("Running benchmarks..."):
                results = []
                test_queries_perf = [
                    "emergency",
                    "medication schedule",
                    "safety protocols"
                ]
                
                for tq in test_queries_perf:
                    try:
                        import time
                        start = time.time()
                        response = httpx.post(
                            f"{client.base_url}/knowledge/search",
                            json={"query": tq, "top_k": 5},
                            timeout=20.0
                        )
                        elapsed = (time.time() - start) * 1000
                        
                        if response.status_code == 200:
                            data = response.json()
                            results.append({
                                "Query": tq,
                                "Results": data["count"],
                                "Time (ms)": round(elapsed, 2)
                            })
                    except:
                        pass
                
                if results:
                    perf_df = pd.DataFrame(results)
                    st.dataframe(perf_df, use_container_width=True)
                    
                    avg_time = perf_df["Time (ms)"].mean()
                    st.metric("Average Query Time", f"{avg_time:.2f} ms")
                else:
                    st.warning("No benchmark results available")
    
    # System diagnostics
    st.divider()
    st.subheader("🔧 System Diagnostics")
    
    diag_col1, diag_col2, diag_col3 = st.columns(3)
    
    with diag_col1:
        if st.button("Test API Connection"):
            try:
                response = httpx.get(f"{client.base_url}/health", timeout=5.0)
                if response.status_code == 200:
                    st.success("✅ API is reachable")
                else:
                    st.error(f"❌ API returned {response.status_code}")
            except:
                st.error("❌ Cannot reach API")
    
    with diag_col2:
        if st.button("Test Vector Store"):
            try:
                response = httpx.get(f"{client.base_url}/knowledge/metrics", timeout=5.0)
                if response.status_code == 200:
                    st.success("✅ Vector store is operational")
                else:
                    st.error("❌ Vector store error")
            except:
                st.error("❌ Cannot access vector store")
    
    with diag_col3:
        if st.button("View Configuration"):
            try:
                response = httpx.get(f"{client.base_url}/knowledge/config", timeout=5.0)
                if response.status_code == 200:
                    config = response.json()
                    st.json(config)
                else:
                    st.error("❌ Cannot fetch config")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <small>
    🧬 RAG System powered by OpenAI Embeddings & ChromaDB<br>
    Semantic search • Vector similarity • Knowledge retrieval
    </small>
</div>
""", unsafe_allow_html=True)
