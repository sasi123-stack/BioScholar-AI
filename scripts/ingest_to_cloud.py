
import os
import sys
import logging
import asyncio

# Add project root to path
sys.path.append(os.getcwd())

from src.indexing.es_client import ElasticsearchClient
from src.indexing.index_manager import IndexManager
from src.indexing.document_indexer import DocumentIndexer
from src.data_pipeline.pubmed_fetcher import PubMedFetcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ingest_data():
    """Ingest data into Cloud Elasticsearch."""
    
    # Cloud Credentials (Injected via Environment Variables by the user running the script)
    host = os.environ.get("ELASTICSEARCH_HOST")
    username = os.environ.get("ELASTICSEARCH_USERNAME")
    password = os.environ.get("ELASTICSEARCH_PASSWORD")
    
    if not host or not username or not password:
        logger.error("❌ Missing Elasticsearch credentials in environment variables.")
        return

    logger.info(f"Connecting to Cloud Elasticsearch: {host}...")

    # Initialize Client
    try:
        # Ensure host has https://
        if not host.startswith("http"):
             host_url = f"https://{host}"
        else:
             host_url = host

        es_client = ElasticsearchClient(
            host=host_url,
            port=443,
            username=username,
            password=password
        )
        
        if not es_client.is_connected():
            logger.error("❌ Failed to connect to Elasticsearch.")
            return
            
        logger.info("✅ Connected to Cloud Elasticsearch!")
        
        # Initialize Managers
        index_manager = IndexManager(es_client)
        document_indexer = DocumentIndexer(es_client)
        
        # 1. Create Indexes
        logger.info("Creating indices...")
        index_manager.setup_default_indices(force=True) # Force to ensure clean slate
        
        # 2. Fetch Data (PubMed)
        logger.info("Fetching articles from PubMed...")
        fetcher = PubMedFetcher(email="student@university.edu") # Default email
        
        # Search queries to populate data
        queries = [
            "cancer immunotherapy",
            "CRISPR gene editing",
            "covid-19 vaccine side effects",
            "alzheimers treatment",
            "diabetes management"
        ]
        
        total_indexed = 0
        
        for query in queries:
            logger.info(f"--- Processing query: '{query}' ---")
            articles = fetcher.search_and_fetch(query, max_results=20)
            
            if articles:
                # Add embeddings placeholder (since we don't have the model loaded locally in this script)
                # In a real pipeline, we'd generate embeddings here. 
                # For now, we'll index text-only search which is 90% of the value.
                for article in articles:
                    article['embedding'] = [0.0] * 768 # Dummy embedding to satisfy mapping
                
                success, failed = document_indexer.index_batch("pubmed_articles", articles)
                total_indexed += success
                logger.info(f"Indexed {success} articles for '{query}'")
            else:
                logger.warning(f"No articles found for '{query}'")
        
        logger.info(f"🎉 Ingestion Complete! Total documents indexed: {total_indexed}")
        
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    ingest_data()
