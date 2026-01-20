"""
RAG Engine - Core retrieval and embedding functionality
"""

import os
import uuid
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
import json

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not installed. Vector store functionality will be limited.")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI not installed. Using local embeddings.")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("sentence-transformers not installed. Local embeddings unavailable.")

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("PyPDF2 not installed. PDF processing disabled.")

from .models import (
    Document, DocumentChunk, SearchResult, RAGMetrics, RAGConfig
)

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Main RAG engine for document processing, embedding, and retrieval.
    """
    
    def __init__(
        self,
        collection_name: str = "ai_companion_knowledge",
        persist_directory: str = None,
        openai_api_key: str = None,
        config: Optional[RAGConfig] = None
    ):
        """Initialize RAG engine with vector store and embedding model."""
        self.config = config or RAGConfig()
        self.collection_name = collection_name
        
        # Setup persist directory
        if persist_directory is None:
            persist_directory = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "vector_store"
            )
        self.persist_directory = persist_directory
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize ChromaDB
        self._init_vector_store()
        
        # Initialize embedding model based on provider
        self.embedding_model = None
        self.openai_client = None
        
        if self.config.embedding_provider == "sentence-transformers":
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                logger.info(f"Loading sentence-transformer model: {self.config.embedding_model}")
                self.embedding_model = SentenceTransformer(self.config.embedding_model)
                logger.info("✅ Sentence-transformer model loaded successfully")
            else:
                logger.error("sentence-transformers not installed. Install with: pip install sentence-transformers")
                raise ImportError("sentence-transformers is required for local embeddings")
        
        elif self.config.embedding_provider == "openai":
            if OPENAI_AVAILABLE and openai_api_key:
                self.openai_client = OpenAI(api_key=openai_api_key)
                logger.info(f"✅ OpenAI client initialized with model: {self.config.embedding_model}")
            else:
                logger.error("OpenAI not available or API key not provided")
                raise ValueError("OpenAI API key required for OpenAI embeddings")
        
        else:
            raise ValueError(f"Unknown embedding provider: {self.config.embedding_provider}")
        
        # Document registry
        self.doc_registry_path = os.path.join(self.persist_directory, "documents.json")
        self.documents: Dict[str, Document] = self._load_document_registry()
    
    def _init_vector_store(self):
        """Initialize ChromaDB vector store."""
        if not CHROMADB_AVAILABLE:
            logger.warning("ChromaDB not available. Using in-memory fallback.")
            self.collection = None
            self._fallback_store = []
            return
        
        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": self.config.similarity_metric}
            )
            logger.info(f"Initialized ChromaDB collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.collection = None
            self._fallback_store = []
    
    def _load_document_registry(self) -> Dict[str, Document]:
        """Load document registry from disk."""
        if not os.path.exists(self.doc_registry_path):
            return {}
        try:
            with open(self.doc_registry_path, 'r') as f:
                data = json.load(f)
                return {doc_id: Document(**doc_data) for doc_id, doc_data in data.items()}
        except Exception as e:
            logger.error(f"Failed to load document registry: {e}")
            return {}
    
    def _save_document_registry(self):
        """Save document registry to disk."""
        try:
            data = {doc_id: doc.model_dump() for doc_id, doc in self.documents.items()}
            with open(self.doc_registry_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save document registry: {e}")
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from various file formats."""
        ext = Path(file_path).suffix.lower()
        
        try:
            if ext == '.txt' or ext == '.md':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif ext == '.pdf':
                if not PDF_AVAILABLE:
                    raise ValueError("PyPDF2 not installed. Cannot process PDF files.")
                
                text = []
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        text.append(page.extract_text())
                return '\n\n'.join(text)
            
            else:
                raise ValueError(f"Unsupported file format: {ext}")
        
        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {e}")
            raise
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap."""
        chunks = []
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        
        # Simple character-based chunking with overlap
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary if possible
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                if break_point > chunk_size * 0.5:  # Only break if we're past halfway
                    chunk = chunk[:break_point + 1]
                    end = start + len(chunk)
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return [c for c in chunks if c]  # Remove empty chunks
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for text chunks using configured provider."""
        
        if self.config.embedding_provider == "sentence-transformers":
            if not self.embedding_model:
                logger.error("Sentence transformer model not loaded")
                raise RuntimeError("Embedding model not initialized")
            
            try:
                # Generate embeddings using sentence-transformers
                embeddings = self.embedding_model.encode(
                    texts,
                    convert_to_numpy=True,
                    show_progress_bar=False
                )
                return embeddings.tolist()
            except Exception as e:
                logger.error(f"Failed to generate embeddings with sentence-transformers: {e}")
                raise
        
        elif self.config.embedding_provider == "openai":
            if not self.openai_client:
                logger.error("OpenAI client not initialized")
                raise RuntimeError("OpenAI client not available")
            
            try:
                # Batch API call for efficiency
                response = self.openai_client.embeddings.create(
                    model=self.config.embedding_model,
                    input=texts
                )
                return [item.embedding for item in response.data]
            except Exception as e:
                logger.error(f"Failed to generate embeddings with OpenAI: {e}")
                raise
        
        else:
            logger.error(f"Unknown embedding provider: {self.config.embedding_provider}")
            raise ValueError(f"Unsupported embedding provider: {self.config.embedding_provider}")
    
    def ingest_document(
        self,
        file_path: str,
        filename: str,
        category: str = "general",
        context: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Document:
        """
        Ingest a document: extract text, chunk, embed, and store.
        """
        logger.info(f"Ingesting document: {filename}")
        
        # Extract text
        text = self.extract_text(file_path)
        
        # Create document record
        doc_id = f"doc_{uuid.uuid4().hex[:12]}"
        document = Document(
            id=doc_id,
            filename=filename,
            content=text[:1000],  # Store preview only
            category=category,
            context=context or "Global",
            metadata=metadata or {}
        )
        
        # Chunk text
        chunks = self.chunk_text(text)
        logger.info(f"Split into {len(chunks)} chunks")
        
        # Generate embeddings
        embeddings = self.get_embeddings(chunks)
        
        # Store in vector database
        chunk_ids = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = f"{doc_id}_chunk_{i}"
            chunk_ids.append(chunk_id)
            
            chunk_metadata = {
                "document_id": doc_id,
                "filename": filename,
                "chunk_index": i,
                "category": category,
                "context": context or "Global",
                **(metadata or {})
            }
            
            if self.collection:
                self.collection.add(
                    ids=[chunk_id],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[chunk_metadata]
                )
            else:
                # Fallback storage
                self._fallback_store.append({
                    "id": chunk_id,
                    "embedding": embedding,
                    "document": chunk,
                    "metadata": chunk_metadata
                })
        
        # Update document with chunk count
        document.metadata["chunk_count"] = len(chunks)
        document.metadata["chunk_ids"] = chunk_ids
        
        # Save to registry
        self.documents[doc_id] = document
        self._save_document_registry()
        
        logger.info(f"Successfully ingested document {doc_id} with {len(chunks)} chunks")
        return document
    
    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        category: Optional[str] = None,
        context: Optional[str] = None,
        score_threshold: Optional[float] = None
    ) -> List[SearchResult]:
        """
        Search for relevant chunks using semantic similarity.
        """
        top_k = top_k or self.config.top_k
        score_threshold = score_threshold or self.config.score_threshold
        
        # Generate query embedding
        query_embedding = self.get_embeddings([query])[0]
        
        # Build filter criteria
        where_filter = {}
        if category:
            where_filter["category"] = category
        if context:
            where_filter["context"] = context
        
        # Search vector store
        if self.collection:
            try:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=where_filter if where_filter else None
                )
                
                search_results = []
                for i in range(len(results['ids'][0])):
                    # Convert distance to similarity score (1 - distance for cosine)
                    score = 1 - results['distances'][0][i]
                    
                    if score >= score_threshold:
                        search_results.append(SearchResult(
                            chunk_id=results['ids'][0][i],
                            document_id=results['metadatas'][0][i]['document_id'],
                            content=results['documents'][0][i],
                            score=score,
                            metadata=results['metadatas'][0][i]
                        ))
                
                return search_results
            
            except Exception as e:
                logger.error(f"Search failed: {e}")
                return []
        else:
            # Fallback: Simple cosine similarity
            logger.warning("Using fallback search (no ChromaDB)")
            return []
    
    def get_metrics(self) -> RAGMetrics:
        """Get RAG system metrics."""
        total_chunks = 0
        categories = {}
        contexts = {}
        
        for doc in self.documents.values():
            chunk_count = doc.metadata.get("chunk_count", 0)
            total_chunks += chunk_count
            
            # Count by category
            categories[doc.category] = categories.get(doc.category, 0) + 1
            
            # Count by context
            ctx = doc.context or "Global"
            contexts[ctx] = contexts.get(ctx, 0) + 1
        
        # Calculate vector store size
        vector_store_size = 0
        if os.path.exists(self.persist_directory):
            for root, dirs, files in os.walk(self.persist_directory):
                vector_store_size += sum(os.path.getsize(os.path.join(root, f)) for f in files)
        
        avg_chunk_size = 0
        if total_chunks > 0:
            avg_chunk_size = self.config.chunk_size
        
        # Get collection count
        embedding_count = 0
        if self.collection:
            try:
                embedding_count = self.collection.count()
            except:
                pass
        
        return RAGMetrics(
            total_documents=len(self.documents),
            total_chunks=total_chunks,
            total_embeddings=embedding_count,
            vector_store_size_mb=vector_store_size / (1024 * 1024),
            average_chunk_size=avg_chunk_size,
            embedding_model=self.config.embedding_model,
            embedding_dimension=self.config.embedding_dimension,
            last_indexed=max(
                [doc.upload_date for doc in self.documents.values()],
                default=None
            ),
            categories=categories,
            contexts=contexts
        )
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document and all its chunks."""
        if doc_id not in self.documents:
            return False
        
        try:
            # Get chunk IDs
            chunk_ids = self.documents[doc_id].metadata.get("chunk_ids", [])
            
            # Delete from vector store
            if self.collection and chunk_ids:
                self.collection.delete(ids=chunk_ids)
            
            # Remove from registry
            del self.documents[doc_id]
            self._save_document_registry()
            
            logger.info(f"Deleted document {doc_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False
    
    def reset(self):
        """Reset the entire RAG system (use with caution)."""
        if self.collection:
            try:
                self.client.delete_collection(self.collection_name)
                self.collection = self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": self.config.similarity_metric}
                )
            except:
                pass
        
        self.documents = {}
        self._save_document_registry()
        logger.warning("RAG system reset completed")
