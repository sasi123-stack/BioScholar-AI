"""Test script for Elasticsearch indexing."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.indexing import ElasticsearchClient, IndexManager, DocumentIndexer
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_elasticsearch_connection():
    """Test Elasticsearch connection."""
    logger.info("=" * 60)
    logger.info("Testing Elasticsearch Connection")
    logger.info("=" * 60)
    
    try:
        es_client = ElasticsearchClient()
        
        if es_client.is_connected():
            logger.info("✅ Connected to Elasticsearch")
            
            # Get cluster health
            health = es_client.get_cluster_health()
            logger.info(f"Cluster status: {health['status']}")
            logger.info(f"Number of nodes: {health['number_of_nodes']}")
            
            return es_client
        else:
            logger.error("❌ Failed to connect")
            return None
            
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        return None


def test_index_management(es_client):
    """Test index management."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Index Management")
    logger.info("=" * 60)
    
    index_manager = IndexManager(es_client)
    
    # Setup default indices
    logger.info("Creating default indices...")
    index_manager.setup_default_indices(force=True)
    
    # List indices
    indices = index_manager.list_indices()
    logger.info(f"✅ Available indices: {', '.join(indices)}")
    
    # Check if indices exist
    for index_name in ["pubmed_articles", "clinical_trials"]:
        exists = index_manager.index_exists(index_name)
        count = index_manager.get_document_count(index_name)
        logger.info(f"  {index_name}: exists={exists}, count={count}")
    
    return index_manager


def test_document_indexing(es_client, index_manager):
    """Test document indexing."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Document Indexing")
    logger.info("=" * 60)
    
    indexer = DocumentIndexer(es_client)
    
    # Load processed data
    data_dir = Path(__file__).parent.parent / "data" / "processed"
    
    # Index PubMed articles
    pubmed_files = list((data_dir / "pubmed").glob("*.json"))
    if pubmed_files:
        logger.info(f"\nIndexing PubMed articles from {pubmed_files[0].name}...")
        
        with open(pubmed_files[0], 'r', encoding='utf-8') as f:
            data = json.load(f)
            articles = data.get('articles', [])
        
        if articles:
            success, failed = indexer.index_batch("pubmed_articles", articles)
            logger.info(f"✅ Indexed {success} PubMed articles ({failed} failed)")
            
            # Refresh index
            index_manager.refresh_index("pubmed_articles")
            
            # Verify count
            count = index_manager.get_document_count("pubmed_articles")
            logger.info(f"  Total documents in index: {count}")
    
    # Index Clinical Trials
    trial_files = list((data_dir / "clinical_trials").glob("*.json"))
    if trial_files:
        logger.info(f"\nIndexing clinical trials from {trial_files[0].name}...")
        
        with open(trial_files[0], 'r', encoding='utf-8') as f:
            data = json.load(f)
            trials = data.get('trials', [])
        
        if trials:
            success, failed = indexer.index_batch("clinical_trials", trials)
            logger.info(f"✅ Indexed {success} clinical trials ({failed} failed)")
            
            # Refresh index
            index_manager.refresh_index("clinical_trials")
            
            # Verify count
            count = index_manager.get_document_count("clinical_trials")
            logger.info(f"  Total documents in index: {count}")
    
    return indexer


def test_document_retrieval(indexer):
    """Test document retrieval."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Document Retrieval")
    logger.info("=" * 60)
    
    # Try to get a PubMed article
    indices_to_test = [
        ("pubmed_articles", "41527838"),  # Example PMID
        ("clinical_trials", "NCT00006389")  # Example NCT ID
    ]
    
    for index_name, doc_id in indices_to_test:
        if indexer.document_exists(index_name, doc_id):
            doc = indexer.get_document(index_name, doc_id)
            if doc:
                logger.info(f"\n✅ Retrieved document {doc_id} from {index_name}")
                logger.info(f"  Title: {doc.get('title', '')[:80]}...")
                logger.info(f"  Type: {doc.get('type')}")
        else:
            logger.info(f"\n⚠️  Document {doc_id} not found in {index_name}")


def main():
    """Run all tests."""
    try:
        # Test 1: Connection
        es_client = test_elasticsearch_connection()
        if not es_client:
            logger.error("Cannot proceed without Elasticsearch connection")
            sys.exit(1)
        
        # Test 2: Index Management
        index_manager = test_index_management(es_client)
        
        # Test 3: Document Indexing
        indexer = test_document_indexing(es_client, index_manager)
        
        # Test 4: Document Retrieval
        test_document_retrieval(indexer)
        
        logger.info("\n" + "=" * 60)
        logger.info("✨ All Elasticsearch tests completed!")
        logger.info("=" * 60)
        
        # Cleanup
        es_client.close()
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
