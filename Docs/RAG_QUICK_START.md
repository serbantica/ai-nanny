# RAG System Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies (1 min)

```bash
cd ai-nanny/ai-companion-orchestrator

# Install core RAG dependencies
pip install chromadb pypdf2 langchain langchain-community tiktoken

# Install local embeddings (FREE - No API key needed!)
pip install sentence-transformers torch
```

**Why sentence-transformers?**
- ✅ 100% Free - No API costs
- ✅ Private - All processing on your machine
- ✅ Fast - No network latency
- ✅ No API key required
### Step 2: Verify Installation (30 sec)

```bash
python3 -c "from core.rag import RAGEngine; print('✅ RAG Ready!')"
```

### Step 3: Start the Backend API (1 min)

```bash
cd ai-nanny/ai-companion-orchestrator
python3 -m uvicorn api.main:app --reload --port 8000
```

Keep this terminal running.

### Step 4: Start the Dashboard (1 min)

In a new terminal:
```bash
cd ai-nanny/dashboard
streamlit run app.py
```

### Step 5: Access RAG Dashboard (30 sec)

1. Open browser: http://localhost:8501
2. Click **"RAG System"** in the left sidebar
3. You should see the RAG dashboard!

---

## 📁 How to Index Documents

### Method 1: Using the Dashboard (Recommended)

**Step-by-step:**

1. **Navigate to Knowledge Base Management**
   - Open dashboard: http://localhost:8501
   - Click **"05_KNOWLEDGE"** page in sidebar
   - You'll see the "Knowledge Management" interface

2. **Upload a Document**
   - Click **"📤 Upload Instructions/Protocol"** button
   - **Choose file**: Select `.txt`, `.md`, or `.pdf` file
   - **Enter filename**: Give it a descriptive name (e.g., "Fall Response Protocol")
   - **Select category**: Choose from dropdown:
     - `emergency` - Emergency procedures, safety protocols
     - `activity` - Activities, exercises, entertainment
     - `health` - Health monitoring, medication, vitals
     - `communication` - Communication guidelines, reporting
     - `general` - Other documents
   - **Context** (optional): Assign to specific persona or leave as "Global"
   - Click **"Ingest Document"** button

3. **Wait for Processing**
   - You'll see: "Processing document..."
   - The system will:
     - Extract text from your document
     - Split it into ~500 character chunks
     - Generate embeddings (sentence-transformers, no API cost!)
     - Store in ChromaDB vector database
   - Time: 2-10 seconds depending on document size
   - Success message: "✅ Document ingested successfully!"

4. **Verify Upload**
   - Go to **"RAG System"** page → **"Knowledge Base"** tab
   - Your document should appear in the list
   - Check the metrics showing chunk count

### Sample Documents Already Available

The system comes with **3 pre-created sample documents** ready to index:

1. **Emergency Protocols** (`data/documents/emergency_protocols.md`)
   - Fall detection & response
   - Medication errors
   - Medical emergencies
   - Safety alerts
   - **Category**: `emergency`
   - **~4,500 words, 30+ chunks**

2. **Activity Guidelines** (`data/documents/activity_guidelines.md`)
   - Physical activities & exercises
   - Cognitive engagement games
   - Social activities
   - Entertainment options
   - **Category**: `activity`
   - **~3,500 words, 25+ chunks**

3. **Health Kinetics Procedures** (`data/documents/health_kinetics_procedures.md`)
   - Vital signs monitoring
   - Movement tracking
   - Physical therapy protocols
   - Health alerts
   - **Category**: `health`
   - **~7,000 words, 50+ chunks**

**To index these sample documents:**
```bash
# Option A: Upload via dashboard (navigate to file path above)

# Option B: Use API directly
cd ai-nanny/ai-companion-orchestrator

# Index emergency protocols
curl -X POST "http://localhost:8000/api/v1/knowledge/ingest" \
  -F "file=@data/documents/emergency_protocols.md" \
  -F "category=emergency"

# Index activity guidelines
curl -X POST "http://localhost:8000/api/v1/knowledge/ingest" \
  -F "file=@data/documents/activity_guidelines.md" \
  -F "category=activity"

# Index health procedures
curl -X POST "http://localhost:8000/api/v1/knowledge/ingest" \
  -F "file=@data/documents/health_kinetics_procedures.md" \
  -F "category=health"
```

---

## 🔍 How to Test Retrieval

### Method 1: Dashboard Semantic Search

1. **Go to RAG System Page**
   - Navigate to **"RAG System"** in sidebar
   - Click **"🔍 Semantic Search"** tab

2. **Configure Search Parameters (Sidebar)**
   - **Embedding Provider**: sentence-transformers (default, free!)
   - **Top K**: 5 (number of results)
   - **Score Threshold**: 0.7 (minimum relevance)

3. **Enter Search Query**
   - Type natural language question in text box
   - Examples:
     - "What are the steps for fall response?"
     - "How do I monitor blood pressure?"
     - "What activities are good for cognitive health?"
     - "Emergency contact procedures"

4. **Apply Filters (Optional)**
   - **Category filter**: Select specific category (emergency, activity, health)
   - **Context filter**: Filter by persona or "Global"

5. **Execute Search**
   - Click **"🔍 Search"** button
   - Results appear below with:
     - **Relevance score** (0-1, higher is better)
     - **Content preview** (actual text chunk)
     - **Source document** (filename)
     - **Category & context** (metadata)

### Method 2: Quick Test Tab

1. **Go to "⚡ Quick Test" tab**
2. **Select a pre-configured test query**:
   - Emergency: "fall detection procedures"
   - Health: "vital signs monitoring"
   - Activity: "cognitive engagement"
3. **Click "Run Test"**
4. See instant results with performance metrics

### Method 3: API Testing

```bash
# Test semantic search via API
curl -X POST "http://localhost:8000/api/v1/knowledge/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What should I do if someone falls?",
    "top_k": 5,
    "score_threshold": 0.7,
    "category": "emergency"
  }' | python3 -m json.tool
```

---

## 📊 How to Evaluate RAG Results

### Understanding Relevance Scores

**Score Range: 0.0 - 1.0**

| Score Range | Quality | Interpretation | Action |
|------------|---------|----------------|--------|
| **0.90-1.00** | Excellent | Near-exact match, highly relevant | Use directly |
| **0.80-0.89** | Very Good | Strong semantic match | Reliable information |
| **0.70-0.79** | Good | Relevant, useful context | Good for context |
| **0.60-0.69** | Fair | Related but not perfect | Review carefully |
| **0.50-0.59** | Poor | Weak connection | May not be useful |
| **< 0.50** | Very Poor | Likely irrelevant | Filtered out by default |

### Evaluation Criteria

**1. Relevance Assessment**
- ✅ **Good Result**: Content directly answers the query
- ✅ **Good Result**: Key terms from query appear in result
- ❌ **Poor Result**: Content is off-topic or tangential

**Example:**
```
Query: "How to respond to a fall?"
Good Result (Score: 0.92):
"Fall Response Protocol: 1) Call for help immediately 
2) Do not move the resident 3) Check for injuries..."

Poor Result (Score: 0.55):
"...residents enjoy walking activities outdoors..."
```

**2. Coverage Evaluation**
- Check if top results cover different aspects of the query
- Look for diverse information, not duplicate chunks
- Verify important details aren't missing

**3. Precision vs Recall**
- **High Precision**: Few results, but all highly relevant (high threshold: 0.8+)
- **High Recall**: Many results, captures everything (low threshold: 0.5+)
- **Balanced**: threshold = 0.7, top_k = 5-10

### Practical Evaluation Steps

**Step 1: Run Test Queries**
```bash
# Test emergency knowledge
Query: "fall emergency response"
Expected: Emergency protocols, call procedures, safety steps

# Test health knowledge  
Query: "blood pressure monitoring"
Expected: Vital signs procedures, normal ranges, alert thresholds

# Test activity knowledge
Query: "physical exercises for seniors"
Expected: Exercise routines, safety guidelines, benefits
```

**Step 2: Check System Metrics**
1. Go to **"System Metrics"** tab
2. Click **"🔄 Refresh Metrics"**
3. Verify:
   - ✅ Documents indexed: 3+ documents
   - ✅ Total chunks: 100+ chunks
   - ✅ Embeddings generated: matches chunk count
   - ✅ Categories populated: emergency, activity, health

**Step 3: Visual Quality Check**
1. Review **"Distribution Charts"**:
   - Documents per category (should be balanced)
   - Chunks per document (should be ~20-50 chunks per doc)
   - Vector store size (grows with more documents)

**Step 4: A/B Testing Different Configurations**

Test different settings to optimize:

| Configuration | Use Case | Settings |
|--------------|----------|----------|
| **Precise** | Finding specific procedures | threshold=0.8, top_k=3 |
| **Balanced** | General questions | threshold=0.7, top_k=5 |
| **Comprehensive** | Exploratory research | threshold=0.6, top_k=10 |

**Step 5: False Positive Check**
- Run intentionally unrelated queries
- Example: Query="weather forecast" when you only have care documents
- **Expected**: No results or very low scores (< 0.5)
- **Problem**: If getting high scores for unrelated content, lower threshold

### Quality Metrics Dashboard

Go to **"System Metrics"** tab to see:

1. **Document Health Indicators**
   - 🟢 Green: System healthy, good coverage
   - 🟡 Yellow: Low document count, need more content
   - 🔴 Red: Critical issues, reindex needed

2. **Search Performance**
   - Average query time (should be < 100ms with local embeddings)
   - Cache hit rate
   - Embedding generation time

3. **Content Coverage**
   - Categories with documents
   - Chunks per category
   - Storage utilization

### Common Issues & Solutions

**Issue: Low Relevance Scores (all < 0.6)**
- **Cause**: Query doesn't match document content
- **Solution**: 
  - Try different phrasing
  - Check if relevant documents are indexed
  - Verify correct category selected

**Issue: Too Many Results, All Similar**
- **Cause**: Duplicate content or repeated chunks
- **Solution**:
  - Increase score threshold (0.8+)
  - Reduce top_k (try 3 instead of 10)
  - Check for duplicate documents in KB

**Issue: No Results Found**
- **Cause**: No documents indexed or threshold too high
- **Solution**:
  - Check System Metrics → Total Documents > 0
  - Lower threshold to 0.5
  - Verify documents are in correct category

**Issue: Wrong Information Retrieved**
- **Cause**: Poor chunking or ambiguous query
- **Solution**:
  - Make query more specific
  - Adjust chunk_size (try 300 or 700)
  - Review source document quality

---

## 🧪 Test the System

### Test 1: Upload a Document

1. Go to **"Knowledge Base"** page in the dashboard
2. Click **"Upload Instructions/Protocol"**
3. Select a `.txt`, `.md`, or `.pdf` file
4. Choose a category
5. Click **"Ingest Document"**
6. Wait for processing (should take 2-10 seconds)

**Sample documents available:**
- `data/documents/emergency_protocols.md`
- `data/documents/activity_guidelines.md`

### Test 2: Semantic Search

1. Go to **"RAG System"** page → **"Semantic Search"** tab
2. Enter a query: `"What should I do if someone falls?"`
3. Click **"🔍 Search"**
4. View results with relevance scores

### Test 3: View Metrics

1. Go to **"System Metrics"** tab
2. Click **"🔄 Refresh Metrics"**
3. See:
   - Total documents
   - Total chunks
   - Vector store size
   - Category distribution

## 📊 Test Queries & Expected Results

After indexing the sample documents, try these queries:

### Emergency Protocols Tests

| Query | Expected Score | Expected Content |
|-------|---------------|------------------|
| "fall detection and response" | 0.85+ | Fall detection steps, response protocol |
| "medication error procedures" | 0.80+ | Medication management, error handling |
| "emergency contact information" | 0.75+ | Emergency contacts, escalation paths |
| "safety alert protocols" | 0.80+ | Alert generation, notification procedures |

### Activity Guidelines Tests

| Query | Expected Score | Expected Content |
|-------|---------------|------------------|
| "physical exercises for seniors" | 0.85+ | Exercise routines, safety guidelines |
| "cognitive games and activities" | 0.82+ | Brain training, memory games |
| "social engagement activities" | 0.78+ | Group activities, social events |
| "morning routine activities" | 0.75+ | Daily schedule, morning exercises |

### Health Procedures Tests

| Query | Expected Score | Expected Content |
|-------|---------------|------------------|
| "blood pressure monitoring" | 0.88+ | Vital signs procedures, normal ranges |
| "movement tracking procedures" | 0.85+ | Activity monitoring, movement analysis |
| "physical therapy protocols" | 0.83+ | Therapy guidelines, exercise protocols |
| "health alert thresholds" | 0.80+ | Alert criteria, escalation rules |

### Cross-Category Tests

| Query | Expected Behavior | Categories |
|-------|------------------|------------|
| "daily care routine" | Results from multiple categories | activity, health, emergency |
| "resident safety" | Emergency + health protocols | emergency, health |
| "monitoring procedures" | Health + activity tracking | health, activity |

## ⚙️ Configuration (Optional)

### Option 1: Local Embeddings (Recommended - FREE!)

Default configuration uses sentence-transformers (no API key needed):

```env
# .env file
RAG_EMBEDDING_PROVIDER=sentence-transformers
RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2
RAG_EMBEDDING_DIMENSION=384
```

**Available Local Models:**
- `all-MiniLM-L6-v2`: Fast, 384 dims (Recommended)
- `all-mpnet-base-v2`: Higher quality, 768 dims
- `paraphrase-multilingual-MiniLM-L12-v2`: Multilingual support

### Option 2: OpenAI Embeddings (Higher Quality - Paid)

If you want the highest quality embeddings:

```env
# Required
OPENAI_API_KEY=sk-your-key-here
APP_SECRET_KEY=your-secret-key-here

# RAG Settings for OpenAI
RAG_EMBEDDING_PROVIDER=openai
RAG_EMBEDDING_MODEL=text-embedding-3-small
RAG_EMBEDDING_DIMENSION=1536
```

# RAG Settings (optional, these are defaults)
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50
RAG_EMBEDDING_MODEL=text-embedding-3-small
RAG_TOP_K=5
RAG_SCORE_THRESHOLD=0.7
```

## 🎯 Key Features to Explore

### 1. Semantic Search Interface
- Natural language queries
- Category and context filtering
- Adjustable parameters (top_k, threshold)
- Relevance scoring

### 2. System Metrics Dashboard
- Document statistics
- Visual analytics (pie charts, bar graphs)
- Health monitoring
- Storage tracking

### 3. Knowledge Base Browser
- View all documents
- Filter by category/context
- Delete documents
- See metadata

### 4. Quick Test Suite
- Sample queries
- Performance benchmarks
- System diagnostics
- API health checks

## 🔍 Common Use Cases

### Use Case 1: Find Emergency Procedures
```
Query: "What to do in a fall emergency?"
Result: Relevant sections from emergency protocols
```

### Use Case 2: Activity Planning
```
Query: "Physical activities for seniors"
Result: Exercise routines, outdoor activities, safety guidelines
```

### Use Case 3: Care Guidelines
```
Query: "Medication administration rules"
Result: Medication management protocols, timing, safety
```

## 📈 Understanding Results

### Relevance Scores
- **0.9-1.0**: Highly relevant, near-exact match
- **0.7-0.9**: Good match, relevant information
- **0.5-0.7**: Moderate match, possibly useful
- **< 0.5**: Low relevance (filtered by default)

### Result Metadata
Each result shows:
- **Filename**: Source document
- **Category**: Document type
- **Context**: Persona or "Global"
- **Chunk Index**: Position in document
- **Score**: Relevance score (0-1)

## 🛠️ Troubleshooting

### Problem: "Cannot connect to API"
**Solution:**
```bash
# Check if API is running
curl http://localhost:8000/health

# If not, start it:
cd ai-companion-orchestrator
python3 -m uvicorn api.main:app --reload --port 8000
```

### Problem: "No results found"
**Solution:**
1. Check if documents are uploaded (go to Knowledge Base tab)
2. Lower the score threshold (try 0.5)
3. Try simpler keywords
4. Check System Metrics to verify embeddings exist

### Problem: "OpenAI API error"
**Solution:**
1. Check `.env` file has `OPENAI_API_KEY`
2. Verify API key is valid
3. Check API usage limits

### Problem: "ChromaDB not initialized"
**Solution:**
```bash
# Reinstall ChromaDB
pip install --force-reinstall chromadb

# Verify installation
python3 -c "import chromadb; print('✅ ChromaDB OK')"
```

## 📚 Next Steps

1. **Upload Your Documents:**
   - Facility protocols
   - Care guidelines
   - Safety procedures
   - Activity schedules

2. **Customize Configuration:**
   - Adjust chunk size for your content
   - Set appropriate score thresholds
   - Configure embedding model

3. **Integrate with Personas:**
   - Assign documents to specific personas
   - Use context filtering in searches
   - Build persona-specific knowledge bases

4. **Monitor Performance:**
   - Check query response times
   - Review relevance scores
   - Optimize parameters as needed

## 🎓 Learning Resources

- **Full Documentation:** `Docs/RAG_IMPLEMENTATION_GUIDE.md`
- **Parameter Reference:** `Docs/RAG_PARAMETER_REFERENCE.md`
- **API Endpoints:** Check `/knowledge/config` endpoint

## 💡 Pro Tips

1. **Better Chunks = Better Results**
   - Use well-structured documents
   - Include clear headings
   - Keep related information together

2. **Optimize Search Queries**
   - Be specific but natural
   - Include key terms
   - Try different phrasings

3. **Use Filters**
   - Filter by category to narrow results
   - Use context for persona-specific searches
   - Combine filters for precision

4. **Monitor Storage**
   - Check vector store size regularly
   - Delete outdated documents
   - Keep knowledge base organized

## ✅ Success Checklist

- [ ] Dependencies installed
- [ ] API server running on port 8000
- [ ] Dashboard accessible at http://localhost:8501
- [ ] RAG System page loads
- [ ] Sample document uploaded successfully
- [ ] Search returns relevant results
- [ ] Metrics show correct counts
- [ ] Health checks pass

## 🆘 Getting Help

If you encounter issues:

1. **Check Logs:**
   ```bash
   # API logs
   tail -f server.log
   
   # Dashboard terminal output
   ```

2. **Test Components:**
   - API: `curl http://localhost:8000/health`
   - Metrics: `curl http://localhost:8000/api/v1/knowledge/metrics`
   - Config: `curl http://localhost:8000/api/v1/knowledge/config`

3. **System Diagnostics:**
   - Go to "Quick Test" tab
   - Run all diagnostic tests
   - Check for errors

## 🎉 You're Ready!

Your RAG system is now set up and ready to enhance the AI Companion platform with powerful semantic search and knowledge retrieval capabilities!

---

**Quick Links:**
- Dashboard: http://localhost:8501
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
