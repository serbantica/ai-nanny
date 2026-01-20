#!/usr/bin/env python3
"""
Bulk document ingestion script for RAG system.
Processes all documents in data/documents/ directory.
"""

import os
import sys
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.rag import RAGEngine
from core.rag.models import RAGConfig
from core.config import get_settings

def ingest_all_documents():
    """Ingest all documents from data/documents/ directory."""
    
    settings = get_settings()
    
    # Initialize RAG engine
    logger.info("Initializing RAG engine...")
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
    
    rag_engine = RAGEngine(
        persist_directory=settings.rag_vector_store_path,
        openai_api_key=settings.openai_api_key if settings.rag_embedding_provider == "openai" else None,
        config=rag_config
    )
    
    logger.info(f"✅ RAG Engine initialized with {settings.rag_embedding_provider} embeddings")
    logger.info(f"   Model: {settings.rag_embedding_model}")
    logger.info(f"   Vector Store: {settings.rag_vector_store_path}")
    
    # Find all documents
    documents_dir = Path(__file__).parent / "data" / "documents"
    
    if not documents_dir.exists():
        logger.error(f"Documents directory not found: {documents_dir}")
        return
    
    # Get all supported files
    supported_extensions = ['.txt', '.md', '.pdf']
    documents = []
    
    for ext in supported_extensions:
        documents.extend(documents_dir.glob(f"*{ext}"))
    
    if not documents:
        logger.warning(f"No documents found in {documents_dir}")
        return
    
    logger.info(f"\n📚 Found {len(documents)} documents to ingest:")
    for doc in documents:
        logger.info(f"   - {doc.name}")
    
    # Ingest each document
    print("\n" + "="*70)
    print("STARTING DOCUMENT INGESTION")
    print("="*70 + "\n")
    
    success_count = 0
    error_count = 0
    
    for doc_path in documents:
        try:
            logger.info(f"\n📄 Processing: {doc_path.name}")
            logger.info(f"   Size: {doc_path.stat().st_size / 1024:.1f} KB")
            
            # Determine category from filename
            filename = doc_path.name.lower()
            if 'emergency' in filename or 'fall' in filename:
                category = "safety"
            elif 'medication' in filename:
                category = "healthcare"
            elif 'activity' in filename or 'daily' in filename:
                category = "activities"
            elif 'communication' in filename:
                category = "communication"
            else:
                category = "general"
            
            # Ingest document
            document = rag_engine.ingest_document(
                file_path=str(doc_path),
                filename=doc_path.name,
                category=category,
                context="Global",
                metadata={
                    "source": "bulk_ingest",
                    "file_size": doc_path.stat().st_size
                }
            )
            
            logger.info(f"   ✅ Success! Created {document.metadata.get('chunk_count', 0)} chunks")
            logger.info(f"   Document ID: {document.id}")
            logger.info(f"   Category: {category}")
            success_count += 1
            
        except Exception as e:
            logger.error(f"   ❌ Failed to ingest {doc_path.name}: {e}")
            error_count += 1
    
    # Summary
    print("\n" + "="*70)
    print("INGESTION COMPLETE")
    print("="*70)
    logger.info(f"\n📊 Summary:")
    logger.info(f"   ✅ Successfully ingested: {success_count} documents")
    if error_count > 0:
        logger.info(f"   ❌ Failed: {error_count} documents")
    logger.info(f"   📦 Total documents in system: {len(rag_engine.documents)}")
    
    # Get metrics
    try:
        metrics = rag_engine.get_metrics()
        logger.info(f"\n📈 RAG System Metrics:")
        logger.info(f"   Total Documents: {metrics.total_documents}")
        logger.info(f"   Total Chunks: {metrics.total_chunks}")
        logger.info(f"   Vector Store Size: {metrics.vector_store_size / 1024 / 1024:.2f} MB")
        logger.info(f"   Embedding Model: {metrics.embedding_model}")
        logger.info(f"   Embedding Dimension: {metrics.embedding_dimension}")
        
        if metrics.documents_by_category:
            logger.info(f"\n   Documents by Category:")
            for cat, count in metrics.documents_by_category.items():
                logger.info(f"      • {cat}: {count}")
    except Exception as e:
        logger.warning(f"Could not retrieve metrics: {e}")
    
    print("\n✨ RAG system is ready for semantic search!")
    print(f"   Test it in the dashboard at: http://localhost:8501/06_RAG_SYSTEM\n")

if __name__ == "__main__":
    try:
        ingest_all_documents()
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Ingestion interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\n❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
