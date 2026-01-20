"""
RAG (Retrieval-Augmented Generation) Module

This module provides document ingestion, embedding, vector storage,
and retrieval capabilities for the AI Companion system.
"""

from .engine import RAGEngine
from .models import Document, DocumentChunk, SearchResult, RAGMetrics

__all__ = ["RAGEngine", "Document", "DocumentChunk", "SearchResult", "RAGMetrics"]
