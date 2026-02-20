"""
FastAPI dependencies for shared resources.
"""

import os
from functools import lru_cache
from typing import Optional

from src.utils.config import Settings
from src.search_engine.hybrid_search import HybridSearchEngine
from src.search_engine.reranker import CrossEncoderReranker
from src.qa_module.qa_engine import QuestionAnsweringEngine
from src.indexing.document_indexer import DocumentIndexer
from src.utils.logger import logger


# Global instances
_settings: Optional[Settings] = None
_search_engine: Optional[HybridSearchEngine] = None
_reranker: Optional[CrossEncoderReranker] = None
_qa_engine: Optional[QuestionAnsweringEngine] = None
_document_indexer: Optional[DocumentIndexer] = None

# Check if running on low-memory environment
IS_LOW_MEMORY = os.getenv('LOW_MEMORY_MODE', 'false').lower() == 'true'


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)."""
    global _settings
    if _settings is None:
        _settings = Settings()
        logger.info("Settings loaded")
    return _settings


def get_search_engine() -> HybridSearchEngine:
    """Get hybrid search engine instance (singleton)."""
    global _search_engine
    if _search_engine is None:
        settings = get_settings()
        _search_engine = HybridSearchEngine(alpha=0.5)
        logger.info("HybridSearchEngine initialized")
    return _search_engine


def get_reranker() -> Optional[CrossEncoderReranker]:
    """Get cross-encoder reranker instance (singleton)."""
    global _reranker
    
    if IS_LOW_MEMORY:
        logger.warning("⚠️ Reranker disabled (LOW_MEMORY_MODE=true)")
        return None
    
    if _reranker is None:
        _reranker = CrossEncoderReranker()
        logger.info("CrossEncoderReranker initialized")
    return _reranker


def get_qa_engine() -> Optional[QuestionAnsweringEngine]:
    """Get question answering engine instance (singleton)."""
    global _qa_engine
    
    if IS_LOW_MEMORY:
        logger.warning("⚠️ QA Engine disabled (LOW_MEMORY_MODE=true)")
        return None
    
    if _qa_engine is None:
        _qa_engine = QuestionAnsweringEngine()
        logger.info("QuestionAnsweringEngine initialized")
    return _qa_engine


def get_document_indexer() -> DocumentIndexer:
    """Get document indexer instance (singleton)."""
    global _document_indexer
    if _document_indexer is None:
        search_engine = get_search_engine()
        _document_indexer = DocumentIndexer(search_engine.es_client)
        logger.info("DocumentIndexer initialized")
    return _document_indexer


def initialize_services():
    """Initialize all services at startup."""
    logger.info("Initializing API services...")
    get_settings()
    get_search_engine()
    
    if not IS_LOW_MEMORY:
        get_reranker()
        get_qa_engine()
        logger.info("✅ All services initialized")
    else:
        logger.warning("⚠️ Running in LOW_MEMORY_MODE - Q&A and reranking disabled")
        logger.info("✅ Core services initialized")


def cleanup_services():
    """Cleanup services on shutdown."""
    global _search_engine, _reranker, _qa_engine
    
    logger.info("Cleaning up API services...")
    
    if _search_engine is not None:
        _search_engine.es_client.close()
        _search_engine = None
    
    _reranker = None
    _qa_engine = None
    
    logger.info("✅ Services cleaned up")
