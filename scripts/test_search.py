"""Test script for search engine functionality."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.search_engine import HybridSearchEngine, CrossEncoderReranker, QueryProcessor
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_query_processing():
    """Test query processing."""
    logger.info("=" * 60)
    logger.info("Testing Query Processing")
    logger.info("=" * 60)
    
    processor = QueryProcessor()
    
    # Test queries
    queries = [
        "COVID-19 treatment",
        "diabetes mellitus treatment",
        "htn medications",
        "cancer immunotherapy"
    ]
    
    for query in queries:
        logger.info(f"\nProcessing: '{query}'")
        result = processor.process_query(query)
        logger.info(f"  Cleaned: {result['cleaned']}")
        logger.info(f"  Expanded: {result['expanded']}")
        logger.info(f"  Keywords: {result['keywords']}")


def test_keyword_search():
    """Test keyword search."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Keyword Search (BM25)")
    logger.info("=" * 60)
    
    search_engine = HybridSearchEngine()
    
    query = "COVID-19 treatment"
    logger.info(f"\nSearching PubMed for: '{query}'")
    
    try:
        results = search_engine.keyword_search('pubmed_articles', query, size=5)
        
        logger.info(f"✅ Found {len(results)} results")
        
        for i, result in enumerate(results, 1):
            source = result['source']
            logger.info(f"\n{i}. {source.get('title', 'No title')}")
            logger.info(f"   Score: {result['score']:.4f}")
            logger.info(f"   ID: {result['id']}")
            
    except Exception as e:
        logger.error(f"Keyword search failed: {e}", exc_info=True)
    
    search_engine.close()


def test_semantic_search():
    """Test semantic search."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Semantic Search")
    logger.info("=" * 60)
    
    search_engine = HybridSearchEngine()
    
    query = "coronavirus therapy"
    logger.info(f"\nSearching PubMed for: '{query}'")
    
    try:
        results = search_engine.semantic_search('pubmed_articles', query, size=5)
        
        logger.info(f"✅ Found {len(results)} results")
        
        for i, result in enumerate(results, 1):
            source = result['source']
            logger.info(f"\n{i}. {source.get('title', 'No title')}")
            logger.info(f"   Similarity: {result['score']:.4f}")
            logger.info(f"   ID: {result['id']}")
            
    except Exception as e:
        logger.error(f"Semantic search failed: {e}", exc_info=True)
    
    search_engine.close()


def test_hybrid_search():
    """Test hybrid search."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Hybrid Search (BM25 + Semantic)")
    logger.info("=" * 60)
    
    search_engine = HybridSearchEngine(alpha=0.5)
    
    # Test different queries
    queries = [
        "COVID-19 treatment",
        "diabetes management",
        "cancer immunotherapy"
    ]
    
    for query in queries:
        logger.info(f"\n{'=' * 40}")
        logger.info(f"Query: '{query}'")
        logger.info(f"{'=' * 40}")
        
        try:
            # Search PubMed
            results = search_engine.search_pubmed(query, size=5)
            
            logger.info(f"✅ Found {len(results)} PubMed results")
            
            for i, result in enumerate(results, 1):
                source = result['source']
                logger.info(f"\n{i}. {source.get('title', 'No title')[:100]}...")
                logger.info(f"   Combined Score: {result['score']:.4f}")
                logger.info(f"   Keyword: {result['keyword_score']:.4f} | Semantic: {result['semantic_score']:.4f}")
                
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}", exc_info=True)
    
    search_engine.close()


def test_reranking():
    """Test cross-encoder reranking."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Cross-Encoder Reranking")
    logger.info("=" * 60)
    
    search_engine = HybridSearchEngine()
    reranker = CrossEncoderReranker()
    
    query = "COVID-19 treatment"
    logger.info(f"\nQuery: '{query}'")
    
    try:
        # Get initial results
        logger.info("Getting initial search results...")
        results = search_engine.search_pubmed(query, size=10)
        
        logger.info(f"Initial top 3 results:")
        for i, result in enumerate(results[:3], 1):
            source = result['source']
            logger.info(f"{i}. {source.get('title', 'No title')[:80]}...")
            logger.info(f"   Score: {result['score']:.4f}")
        
        # Rerank results
        logger.info("\nReranking results...")
        reranked = reranker.rerank(query, results, top_k=10)
        
        logger.info(f"\nReranked top 3 results:")
        for i, result in enumerate(reranked[:3], 1):
            source = result['source']
            logger.info(f"{i}. {source.get('title', 'No title')[:80]}...")
            logger.info(f"   Original: {result['score']:.4f} | Rerank: {result['rerank_score']:.4f} | Final: {result['final_score']:.4f}")
        
    except Exception as e:
        logger.error(f"Reranking test failed: {e}", exc_info=True)
    
    search_engine.close()


def test_clinical_trials_search():
    """Test clinical trials search."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Clinical Trials Search")
    logger.info("=" * 60)
    
    search_engine = HybridSearchEngine()
    
    query = "diabetes treatment"
    logger.info(f"\nSearching clinical trials for: '{query}'")
    
    try:
        results = search_engine.search_clinical_trials(query, size=5)
        
        logger.info(f"✅ Found {len(results)} results")
        
        for i, result in enumerate(results, 1):
            source = result['source']
            logger.info(f"\n{i}. {source.get('title', 'No title')[:100]}...")
            logger.info(f"   Score: {result['score']:.4f}")
            logger.info(f"   ID: {result['id']}")
            
    except Exception as e:
        logger.error(f"Clinical trials search failed: {e}", exc_info=True)
    
    search_engine.close()


def main():
    """Main test execution."""
    try:
        # Test 1: Query Processing
        test_query_processing()
        
        # Test 2: Keyword Search
        test_keyword_search()
        
        # Test 3: Semantic Search
        test_semantic_search()
        
        # Test 4: Hybrid Search
        test_hybrid_search()
        
        # Test 5: Reranking
        test_reranking()
        
        # Test 6: Clinical Trials
        test_clinical_trials_search()
        
        logger.info("\n" + "=" * 60)
        logger.info("✨ All search tests completed!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
