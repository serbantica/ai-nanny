# RAG System Implementation Guide

## Overview

The AI Nanny project now includes a comprehensive **RAG (Retrieval-Augmented Generation)** system that enables semantic search and knowledge retrieval across documents for devices, personas, and general information.

## Architecture

### Components

1. **RAG Engine** (`core/rag/engine.py`)
   - Document ingestion and text extraction
   - Text chunking with configurable overlap
   - OpenAI embeddings generation
   - ChromaDB vector storage
   - Semantic search capabilities

2. **Data Models** (`core/rag/models.py`)
   - Document, DocumentChunk, SearchResult
   - RAGMetrics for system monitoring
   - RAGConfig for parameter management

3. **API Endpoints** (`api/routers/knowledge.py`)
   - `POST /knowledge/ingest` - Upload and process documents
   - `POST /knowledge/search` - Semantic search
   - `GET /knowledge/metrics` - System statistics
   - `GET /knowledge/config` - Configuration details
   - `DELETE /knowledge/documents/{doc_id}` - Delete documents

4. **Dashboard** (`dashboard/pages/06_RAG_SYSTEM.py`)
   - Semantic search interface
   - System metrics visualization
   - Knowledge base browser
   - Performance testing suite

## Installation

### 1. Install Dependencies

```bash
cd ai-nanny/ai-companion-orchestrator
pip install chromadb pypdf2 langchain langchain-community tiktoken
```

Or update your environment:
```bash
pdm install  # If using PDM
# or
pip install -e .
```

### 2. Configure Environment Variables

Add to your `.env` file:

```env
# Existing OpenAI key will be used for embeddings
OPENAI_API_KEY=sk-your-key-here

# Optional: Custom RAG settings
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50
RAG_EMBEDDING_MODEL=text-embedding-3-small
RAG_EMBEDDING_DIMENSION=1536
RAG_TOP_K=5
RAG_SCORE_THRESHOLD=0.7
RAG_VECTOR_STORE_PATH=data/vector_store
RAG_SIMILARITY_METRIC=cosine
```

### 3. Create Required Directories

```bash
mkdir -p data/vector_store
mkdir -p data/documents
```

## Configuration Parameters

### Chunking Parameters

- **chunk_size** (default: 500)
  - Size of text chunks in characters
  - Larger chunks provide more context but less granular retrieval
  - Recommended: 300-1000 for general documents

- **chunk_overlap** (default: 50)
  - Overlap between consecutive chunks
  - Helps maintain context at chunk boundaries
  - Recommended: 10-20% of chunk_size

### Embedding Settings

- **embedding_model** (default: "text-embedding-3-small")
  - OpenAI embedding model to use
  - Options:
    - `text-embedding-3-small`: Fast, cost-effective (1536 dims)
    - `text-embedding-3-large`: Higher quality (3072 dims)
    - `text-embedding-ada-002`: Legacy model

- **embedding_dimension** (default: 1536)
  - Dimension of embedding vectors
  - Must match selected model

### Search Parameters

- **top_k** (default: 5)
  - Number of results to return
  - Higher values provide more context but may include less relevant results

- **score_threshold** (default: 0.7)
  - Minimum similarity score (0.0 to 1.0)
  - Higher threshold = more relevant but fewer results
  - Recommended: 0.6-0.8 for most use cases

- **similarity_metric** (default: "cosine")
  - Distance metric for similarity calculation
  - Options: cosine, euclidean, dot

## Usage

### Starting the Services

1. **Start the Backend API**:
   ```bash
   cd ai-nanny/ai-companion-orchestrator
   python3 -m uvicorn api.main:app --reload --port 8000
   ```

2. **Start the Dashboard**:
   ```bash
   cd ai-nanny/dashboard
   streamlit run app.py
   ```

3. **Access the RAG Dashboard**:
   - Open browser to http://localhost:8501
   - Navigate to "RAG System" page in sidebar

### Document Ingestion

#### Via Dashboard
1. Go to "RAG System" page
2. Navigate to "Knowledge Base" tab
3. Upload documents (.txt, .md, .pdf)
4. Assign category and context (persona)
5. System automatically:
   - Extracts text
   - Chunks content
   - Generates embeddings
   - Stores in vector database

#### Via API
```python
import httpx

files = {"file": open("document.pdf", "rb")}
data = {
    "category": "Behavioral Guidelines",
    "persona_id": "companion_001"  # Optional
}

response = httpx.post(
    "http://localhost:8000/api/v1/knowledge/ingest",
    files=files,
    data=data
)
```

### Semantic Search

#### Via Dashboard
1. Go to "Semantic Search" tab
2. Enter natural language query
3. Optionally filter by category/context
4. Adjust search parameters (top_k, threshold)
5. View ranked results with relevance scores

#### Via API
```python
import httpx

search_request = {
    "query": "What are the emergency protocols for falls?",
    "top_k": 5,
    "score_threshold": 0.7,
    "category": "Facility Protocols",  # Optional
    "context": "companion_001"  # Optional
}

response = httpx.post(
    "http://localhost:8000/api/v1/knowledge/search",
    json=search_request
)

results = response.json()
print(f"Found {results['count']} results in {results['execution_time_ms']}ms")

for result in results['results']:
    print(f"Score: {result['score']:.3f}")
    print(f"Content: {result['content'][:200]}...")
```

### Monitoring Metrics

```python
import httpx

response = httpx.get("http://localhost:8000/api/v1/knowledge/metrics")
metrics = response.json()

print(f"Total Documents: {metrics['total_documents']}")
print(f"Total Chunks: {metrics['total_chunks']}")
print(f"Total Embeddings: {metrics['total_embeddings']}")
print(f"Vector Store Size: {metrics['vector_store_size_mb']:.2f} MB")
```

## Dashboard Features

### 1. Semantic Search Tab
- **Query Interface**: Natural language search with real-time results
- **Filters**: Category and context/persona filtering
- **Custom Parameters**: Override default search settings
- **Result Display**: Ranked results with:
  - Relevance scores
  - Source document metadata
  - Chunk content preview
  - Visual relevance bars

### 2. System Metrics Tab
- **Key Metrics**: Documents, chunks, embeddings, storage size
- **Visualizations**:
  - Document distribution by category (pie chart)
  - Document distribution by context (bar chart)
- **System Health**: Status indicators for:
  - Document loading
  - Embedding synchronization
  - Storage utilization

### 3. Knowledge Base Tab
- **Document Browser**: Tabular view of all documents
- **Filtering**: Multi-select filters for category and context
- **Document Management**: Delete documents and their embeddings
- **Metadata Display**: Filename, chunk count, upload date

### 4. Quick Test Tab
- **Sample Queries**: Pre-configured test queries
- **Performance Benchmarks**: Multi-query performance testing
- **System Diagnostics**: Health checks for API, vector store, config

## Best Practices

### Document Preparation

1. **Clean Text**: Remove unnecessary formatting, headers, footers
2. **Structured Content**: Use clear headings and sections
3. **Consistent Format**: Maintain similar document structure
4. **Appropriate Length**: 1-50 pages ideal per document

### Chunking Strategy

- **Narrative Content**: Larger chunks (800-1200) maintain story flow
- **Technical Docs**: Medium chunks (400-600) balance detail and context
- **Q&A/FAQs**: Smaller chunks (200-400) for precise matching

### Search Optimization

1. **Use Natural Language**: Write queries as questions or statements
2. **Be Specific**: Include relevant context in queries
3. **Adjust Threshold**: Lower for broader results, raise for precision
4. **Use Filters**: Narrow results with category/context filters

### Performance Tuning

- **Batch Ingestion**: Upload multiple documents at once when possible
- **Monitor Storage**: Keep vector store under 1GB for optimal performance
- **Prune Old Documents**: Regularly remove outdated content
- **Test Queries**: Use Quick Test tab to benchmark performance

## Integration with Personas

RAG enhances persona capabilities by providing:

1. **Context-Specific Knowledge**:
   ```python
   # Assign documents to specific personas
   search_request = {
       "query": "medication reminders",
       "context": "medication_nurse"
   }
   ```

2. **Dynamic Responses**: Personas can reference factual information
3. **Consistent Information**: All personas access same knowledge base
4. **Personalized Filtering**: Each persona queries relevant subset

## Troubleshooting

### Issue: "ChromaDB not available"
**Solution**: Install ChromaDB
```bash
pip install chromadb
```

### Issue: "OpenAI embeddings failed"
**Solution**: Check API key in `.env` file
```bash
echo $OPENAI_API_KEY
```

### Issue: "No results found"
**Solutions**:
- Lower score_threshold (try 0.5)
- Check if documents are ingested
- Verify query relevance to document content

### Issue: "Slow search performance"
**Solutions**:
- Reduce top_k value
- Check vector store size
- Restart API server
- Consider using smaller embedding model

### Issue: "PDF processing fails"
**Solution**: Install PyPDF2
```bash
pip install pypdf2
```

## Advanced Features

### Custom Embedding Models

To use different embedding providers:

1. Modify `core/rag/engine.py`
2. Implement custom embedding function
3. Update configuration

### Reranking

Enable semantic reranking for improved relevance:

```python
# In RAGConfig
rerank = True
```

### Metadata Filtering

Add custom metadata during ingestion:

```python
metadata = {
    "author": "Dr. Smith",
    "date": "2024-01-15",
    "department": "Geriatric Care"
}
```

### Hybrid Search

Combine semantic search with keyword search for better results.

## API Reference

### POST /knowledge/ingest
Ingest a document into RAG system.

**Parameters**:
- `file`: File upload (txt, md, pdf)
- `category`: Document category
- `persona_id`: Optional persona context

**Response**:
```json
{
  "id": "doc_abc123",
  "filename": "protocols.pdf",
  "status": "processed",
  "chunk_count": 45,
  "category": "Facility Protocols",
  "context": "Global",
  "upload_date": "2024-01-19"
}
```

### POST /knowledge/search
Semantic search across knowledge base.

**Request**:
```json
{
  "query": "emergency protocols",
  "top_k": 5,
  "score_threshold": 0.7,
  "category": "Facility Protocols",
  "context": "companion_001"
}
```

**Response**:
```json
{
  "results": [
    {
      "chunk_id": "doc_abc123_chunk_0",
      "document_id": "doc_abc123",
      "content": "In case of emergency...",
      "score": 0.92,
      "metadata": {...}
    }
  ],
  "query": "emergency protocols",
  "count": 5,
  "execution_time_ms": 145.32
}
```

### GET /knowledge/metrics
Get system metrics.

**Response**:
```json
{
  "total_documents": 10,
  "total_chunks": 450,
  "total_embeddings": 450,
  "vector_store_size_mb": 12.5,
  "average_chunk_size": 500,
  "embedding_dimension": 1536,
  "last_indexed": "2024-01-19T10:30:00",
  "categories": {"Protocols": 5, "Guidelines": 5},
  "contexts": {"Global": 7, "companion_001": 3}
}
```

### GET /knowledge/config
Get current RAG configuration.

**Response**:
```json
{
  "chunk_size": 500,
  "chunk_overlap": 50,
  "embedding_model": "text-embedding-3-small",
  "embedding_dimension": 1536,
  "top_k": 5,
  "score_threshold": 0.7,
  "similarity_metric": "cosine",
  "vector_store_path": "data/vector_store"
}
```

### DELETE /knowledge/documents/{doc_id}
Delete a document and its embeddings.

**Response**:
```json
{
  "status": "success",
  "message": "Document doc_abc123 deleted"
}
```

## Future Enhancements

1. **Multi-modal RAG**: Support for images, audio transcripts
2. **Hybrid Search**: Combine semantic + keyword search
3. **Query Expansion**: Automatic query augmentation
4. **Feedback Loop**: Learn from user interactions
5. **Cross-lingual**: Support multiple languages
6. **Real-time Updates**: Live document indexing
7. **Advanced Reranking**: ML-based result refinement

## Support

For issues or questions:
1. Check this guide
2. Review API documentation
3. Test with Quick Test suite
4. Check system diagnostics
5. Review application logs

## License

MIT License - See project root for details
