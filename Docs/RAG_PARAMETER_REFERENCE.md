# RAG Parameter Quick Reference

## Essential Parameters

### 📐 Chunking Parameters

| Parameter | Default | Range | Impact | When to Adjust |
|-----------|---------|-------|--------|----------------|
| **chunk_size** | 500 | 100-2000 | Controls how much text in each chunk | ↑ for narrative docs, ↓ for Q&A |
| **chunk_overlap** | 50 | 0-500 | Overlap between chunks | ↑ for better context preservation |

**Recommended Combinations:**
- **Short FAQs**: chunk_size=200, overlap=20
- **General Docs**: chunk_size=500, overlap=50
- **Long Stories**: chunk_size=1000, overlap=100
- **Technical**: chunk_size=400, overlap=60

### 🎯 Embedding Settings

| Parameter | Options | Trade-offs |
|-----------|---------|------------|
| **embedding_model** | `text-embedding-3-small` (default) | Fast, cost-effective |
|  | `text-embedding-3-large` | Higher quality, 2x cost |
|  | `text-embedding-ada-002` | Legacy, stable |

**Dimensions:**
- 3-small: 1536 dims
- 3-large: 3072 dims
- ada-002: 1536 dims

### 🔍 Search Parameters

| Parameter | Default | Range | Effect | Optimization Tip |
|-----------|---------|-------|--------|------------------|
| **top_k** | 5 | 1-50 | Number of results | ↑ for exploratory, ↓ for precision |
| **score_threshold** | 0.7 | 0.0-1.0 | Minimum relevance | ↓ for more results, ↑ for quality |

**Score Interpretation:**
- **0.9-1.0**: Highly relevant, nearly identical content
- **0.7-0.9**: Good match, relevant information
- **0.5-0.7**: Moderate match, may be useful
- **Below 0.5**: Low relevance, likely not useful

### 📊 Similarity Metrics

| Metric | Best For | Characteristics |
|--------|----------|-----------------|
| **cosine** (default) | General text | Angle-based, normalized |
| **euclidean** | Spatial proximity | Distance-based |
| **dot** | Fast comparisons | Inner product |

## Configuration Presets

### 🎯 High Precision (Legal, Medical)
```env
RAG_CHUNK_SIZE=300
RAG_CHUNK_OVERLAP=30
RAG_EMBEDDING_MODEL=text-embedding-3-large
RAG_TOP_K=3
RAG_SCORE_THRESHOLD=0.85
```
**Use when**: Accuracy is critical, false positives are costly

### ⚡ Balanced (General Purpose)
```env
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50
RAG_EMBEDDING_MODEL=text-embedding-3-small
RAG_TOP_K=5
RAG_SCORE_THRESHOLD=0.7
```
**Use when**: Standard documents, moderate volume

### 🔎 High Recall (Exploratory)
```env
RAG_CHUNK_SIZE=800
RAG_CHUNK_OVERLAP=100
RAG_EMBEDDING_MODEL=text-embedding-3-small
RAG_TOP_K=10
RAG_SCORE_THRESHOLD=0.5
```
**Use when**: Need comprehensive coverage, missing results

### 🚀 Fast & Cheap (Development)
```env
RAG_CHUNK_SIZE=400
RAG_CHUNK_OVERLAP=40
RAG_EMBEDDING_MODEL=text-embedding-3-small
RAG_TOP_K=3
RAG_SCORE_THRESHOLD=0.6
```
**Use when**: Testing, prototyping, cost-sensitive

## Tuning Guide

### Problem: No Results Found
**Solutions:**
1. ↓ Lower score_threshold to 0.5-0.6
2. ↑ Increase top_k to 10-15
3. ↑ Increase chunk_overlap to preserve context
4. Rephrase query with different terms

### Problem: Too Many Irrelevant Results
**Solutions:**
1. ↑ Raise score_threshold to 0.8-0.9
2. ↓ Decrease top_k to 3-5
3. Use category/context filters
4. Make query more specific

### Problem: Missing Context
**Solutions:**
1. ↑ Increase chunk_size to 700-1000
2. ↑ Increase chunk_overlap to 100-150
3. Review document chunking strategy

### Problem: Slow Performance
**Solutions:**
1. ↓ Decrease top_k to 3-5
2. Switch to `text-embedding-3-small`
3. Add category/context filters
4. Prune old documents

### Problem: High Costs
**Solutions:**
1. Use `text-embedding-3-small` instead of large
2. ↓ Reduce chunk_overlap
3. ↓ Increase chunk_size (fewer chunks)
4. Batch document processing

## Performance Benchmarks

### Expected Response Times
- **Search Query**: 50-200ms (local ChromaDB)
- **Document Ingestion**: 1-5 seconds per page
- **Embedding Generation**: 100-500ms per batch

### Resource Usage
| Documents | Chunks | Storage (MB) | RAM (MB) |
|-----------|--------|--------------|----------|
| 10 | 500 | 5-15 | 100-200 |
| 50 | 2,500 | 25-75 | 200-400 |
| 100 | 5,000 | 50-150 | 400-800 |
| 500 | 25,000 | 250-750 | 1000-2000 |

## Quick Setup Commands

```bash
# Install dependencies
pip install chromadb pypdf2 langchain tiktoken

# Create directories
mkdir -p data/vector_store data/documents

# Set environment variables
export RAG_CHUNK_SIZE=500
export RAG_CHUNK_OVERLAP=50
export RAG_EMBEDDING_MODEL=text-embedding-3-small
export RAG_TOP_K=5
export RAG_SCORE_THRESHOLD=0.7

# Start services
cd ai-nanny/ai-companion-orchestrator
uvicorn api.main:app --reload --port 8000

# In another terminal
cd ai-nanny/dashboard
streamlit run app.py
```

## Testing Checklist

- [ ] API health check: `curl http://localhost:8000/health`
- [ ] Vector store initialized: Check `/knowledge/metrics`
- [ ] Upload test document: Use dashboard or API
- [ ] Run test search: "emergency protocols"
- [ ] Check metrics: Document count > 0
- [ ] Verify embeddings: total_embeddings == total_chunks
- [ ] Test filters: Category and context filtering
- [ ] Performance test: < 200ms average query time

## Common .env Template

```env
# Core Settings
OPENAI_API_KEY=sk-your-key-here
APP_SECRET_KEY=your-secret-key-here

# RAG Configuration
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50
RAG_EMBEDDING_MODEL=text-embedding-3-small
RAG_EMBEDDING_DIMENSION=1536
RAG_TOP_K=5
RAG_SCORE_THRESHOLD=0.7
RAG_VECTOR_STORE_PATH=data/vector_store
RAG_SIMILARITY_METRIC=cosine
```

## Dashboard Navigation

1. **Main Menu** → "RAG System"
2. **Tabs**:
   - 🔍 Semantic Search - Query interface
   - 📊 System Metrics - Statistics & health
   - 📚 Knowledge Base - Document browser
   - ⚡ Quick Test - Testing suite

## API Endpoints Quick Access

```bash
# Search
curl -X POST http://localhost:8000/api/v1/knowledge/search \
  -H "Content-Type: application/json" \
  -d '{"query": "emergency protocols", "top_k": 5}'

# Metrics
curl http://localhost:8000/api/v1/knowledge/metrics

# Config
curl http://localhost:8000/api/v1/knowledge/config

# Upload (use multipart/form-data)
curl -X POST http://localhost:8000/api/v1/knowledge/ingest \
  -F "file=@document.pdf" \
  -F "category=Protocols"
```

## Optimization Matrix

| Goal | chunk_size | overlap | model | top_k | threshold |
|------|-----------|---------|-------|-------|-----------|
| **Accuracy** | ↓ Small | ↑ High | Large | ↓ Low | ↑ High |
| **Speed** | ↑ Large | ↓ Low | Small | ↓ Low | ↔ Med |
| **Coverage** | ↑ Large | ↑ High | Small | ↑ High | ↓ Low |
| **Cost** | ↑ Large | ↓ Low | Small | ↓ Low | ↑ High |

---

**Pro Tip**: Start with defaults, measure performance, then adjust one parameter at a time based on specific needs.
