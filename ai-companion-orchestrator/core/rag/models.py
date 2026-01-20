"""
RAG Data Models
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class Document(BaseModel):
    """Document metadata model."""
    id: str
    filename: str
    content: str
    category: str = "general"
    context: Optional[str] = None  # persona_id or "Global"
    upload_date: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentChunk(BaseModel):
    """Document chunk with embedding."""
    id: str
    document_id: str
    chunk_index: int
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchResult(BaseModel):
    """Search result from vector store."""
    chunk_id: str
    document_id: str
    content: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RAGMetrics(BaseModel):
    """RAG system metrics."""
    total_documents: int = 0
    total_chunks: int = 0
    total_embeddings: int = 0
    vector_store_size_mb: float = 0.0
    average_chunk_size: int = 0
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 0
    last_indexed: Optional[str] = None
    categories: Dict[str, int] = Field(default_factory=dict)
    contexts: Dict[str, int] = Field(default_factory=dict)


class RAGConfig(BaseModel):
    """RAG configuration parameters."""
    chunk_size: int = 500
    chunk_overlap: int = 50
    embedding_provider: str = "sentence-transformers"  # "openai" or "sentence-transformers"
    embedding_model: str = "all-MiniLM-L6-v2"  # Model name based on provider
    embedding_dimension: int = 384  # Dimension based on model
    similarity_metric: str = "cosine"
    top_k: int = 5
    score_threshold: float = 0.7
    rerank: bool = False
