from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Query
from typing import List, Optional
from pydantic import BaseModel
import os
from datetime import datetime
import shutil
import logging

from core.local_store import LocalStore # Import persistence helper
from core.rag import RAGEngine
from core.rag.models import SearchResult, RAGMetrics, RAGConfig
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()

# Initialize RAG engine (singleton pattern)
_rag_engine = None

def get_rag_engine() -> RAGEngine:
    """Get or create RAG engine instance."""
    global _rag_engine
    if _rag_engine is None:
        rag_config = RAGConfig(
            chunk_size=settings.rag_chunk_size,
            chunk_overlap=settings.rag_chunk_overlap,
            embedding_provider=settings.rag_embedding_provider,
            embedding_model=settings.rag_embedding_model,
            embedding_dimension=settings.rag_embedding_dimension,
            top_k=settings.rag_top_k,
            score_threshold=settings.rag_score_threshold,
            similarity_metric=settings.rag_similarity_metric
        )
        _rag_engine = RAGEngine(
            persist_directory=settings.rag_vector_store_path,
            openai_api_key=settings.openai_api_key if settings.rag_embedding_provider == "openai" else None,
            config=rag_config
        )
    return _rag_engine

class DocumentResponse(BaseModel):
    id: str
    filename: str
    status: str
    chunk_count: int
    category: Optional[str] = "general"
    context: Optional[str] = None
    upload_date: Optional[str] = None

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = None
    category: Optional[str] = None
    context: Optional[str] = None
    score_threshold: Optional[float] = None

class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    count: int
    execution_time_ms: float

@router.get("/history", response_model=List[DocumentResponse])
async def get_ingestion_history():
    """Get history of ingested documents."""
    docs = LocalStore.get_documents()
    return docs

@router.post("/ingest", response_model=DocumentResponse)
async def ingest_document(
    file: UploadFile = File(...),
    persona_id: Optional[str] = Form(None),
    category: str = Form("general")
):
    """
    Ingest a document into the RAG knowledge base.
    Now uses full RAG pipeline: extract -> chunk -> embed -> store.
    """
    if not file.filename.endswith(('.txt', '.md', '.pdf')):
        raise HTTPException(400, "Only .txt, .md, and .pdf files supported")
    
    # Save file to disk temporarily
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data/documents")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Use RAG engine to process document
        rag_engine = get_rag_engine()
        document = rag_engine.ingest_document(
            file_path=file_path,
            filename=file.filename,
            category=category,
            context=persona_id or "Global",
            metadata={"source": "api_upload"}
        )
        
        # Create response
        doc_meta = {
            "id": document.id,
            "filename": document.filename,
            "status": "processed",
            "chunk_count": document.metadata.get("chunk_count", 0),
            "category": document.category,
            "context": document.context,
            "upload_date": document.upload_date
        }
        
        # Save to local store for UI display
        LocalStore.add_document(doc_meta)
        
        logger.info(f"Successfully ingested document: {file.filename}")
        return DocumentResponse(**doc_meta)
    
    except Exception as e:
        logger.error(f"Failed to ingest document: {e}")
        raise HTTPException(500, f"Document ingestion failed: {str(e)}")

@router.post("/train")
async def train_knowledge_base(persona_id: Optional[str] = None):
    """
    Trigger a specialized training/finetuning job or re-indexing.
    """
    return {
        "status": "success", 
        "message": f"Knowledge base updated {'for ' + persona_id if persona_id else '(Global)'}"
    }

@router.post("/search", response_model=SearchResponse)
async def search_knowledge(request: SearchRequest):
    """
    Semantic search across the knowledge base using RAG.
    """
    import time
    start_time = time.time()
    
    try:
        rag_engine = get_rag_engine()
        results = rag_engine.search(
            query=request.query,
            top_k=request.top_k,
            category=request.category,
            context=request.context,
            score_threshold=request.score_threshold
        )
        
        execution_time = (time.time() - start_time) * 1000
        
        return SearchResponse(
            results=results,
            query=request.query,
            count=len(results),
            execution_time_ms=round(execution_time, 2)
        )
    
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(500, f"Search failed: {str(e)}")

@router.get("/metrics", response_model=RAGMetrics)
async def get_rag_metrics():
    """
    Get RAG system metrics and statistics.
    """
    try:
        rag_engine = get_rag_engine()
        metrics = rag_engine.get_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(500, f"Failed to get metrics: {str(e)}")

@router.get("/config")
async def get_rag_config():
    """
    Get current RAG configuration.
    """
    return {
        "chunk_size": settings.rag_chunk_size,
        "chunk_overlap": settings.rag_chunk_overlap,
        "embedding_model": settings.rag_embedding_model,
        "embedding_dimension": settings.rag_embedding_dimension,
        "top_k": settings.rag_top_k,
        "score_threshold": settings.rag_score_threshold,
        "similarity_metric": settings.rag_similarity_metric,
        "vector_store_path": settings.rag_vector_store_path
    }

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """
    Delete a document from the RAG system.
    """
    try:
        rag_engine = get_rag_engine()
        success = rag_engine.delete_document(doc_id)
        
        if not success:
            raise HTTPException(404, f"Document {doc_id} not found")
        
        return {"status": "success", "message": f"Document {doc_id} deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(500, f"Failed to delete document: {str(e)}")
