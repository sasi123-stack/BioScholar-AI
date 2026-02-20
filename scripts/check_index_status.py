"""Check indexing status and document counts."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.indexing import ElasticsearchClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


def check_status():
    """Check current index status."""
    es = ElasticsearchClient()
    
    logger.info("=" * 60)
    logger.info("📊 ELASTICSEARCH INDEX STATUS")
    logger.info("=" * 60)
    
    # Check PubMed articles
    try:
        pubmed_count = es.client.count(index='pubmed_articles')['count']
        logger.info(f"\n📚 PubMed Articles: {pubmed_count}")
        
        # Get sample document
        if pubmed_count > 0:
            sample = es.client.search(
                index='pubmed_articles',
                body={"query": {"match_all": {}}, "size": 1}
            )
            if sample['hits']['hits']:
                doc = sample['hits']['hits'][0]['_source']
                logger.info(f"  Sample: {doc.get('title', 'N/A')[:80]}...")
                
    except Exception as e:
        logger.warning(f"❌ PubMed index: {e}")
    
    # Check Clinical Trials
    try:
        trials_count = es.client.count(index='clinical_trials')['count']
        logger.info(f"\n🧪 Clinical Trials: {trials_count}")
        
        # Get sample document
        if trials_count > 0:
            sample = es.client.search(
                index='clinical_trials',
                body={"query": {"match_all": {}}, "size": 1}
            )
            if sample['hits']['hits']:
                doc = sample['hits']['hits'][0]['_source']
                logger.info(f"  Sample: {doc.get('title', 'N/A')[:80]}...")
                
    except Exception as e:
        logger.warning(f"❌ Clinical Trials index: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"✅ Total Documents: {pubmed_count + trials_count}")
    logger.info("=" * 60)


if __name__ == "__main__":
    check_status()
