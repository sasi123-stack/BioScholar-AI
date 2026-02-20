"""Test script for data acquisition pipeline."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_pipeline import PubMedFetcher, ClinicalTrialsFetcher, DataStorage
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_pubmed():
    """Test PubMed fetcher."""
    logger.info("=" * 60)
    logger.info("Testing PubMed Fetcher")
    logger.info("=" * 60)
    
    fetcher = PubMedFetcher()
    
    # Test search
    query = "COVID-19 treatment"
    articles = fetcher.search_and_fetch(query, max_results=5)
    
    if articles:
        logger.info(f"\n✅ Successfully fetched {len(articles)} articles")
        logger.info("\nFirst article:")
        first = articles[0]
        logger.info(f"  PMID: {first['pmid']}")
        logger.info(f"  Title: {first['title'][:100]}...")
        logger.info(f"  Journal: {first['journal']}")
        logger.info(f"  Year: {first['publication_year']}")
        logger.info(f"  Authors: {', '.join(first['authors'][:3])}...")
        
        # Save to storage
        storage = DataStorage()
        filepath = storage.save_pubmed_articles(articles, query)
        logger.info(f"\n💾 Saved to: {filepath}")
    else:
        logger.warning("❌ No articles found")


def test_clinical_trials():
    """Test ClinicalTrials fetcher."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing ClinicalTrials.gov Fetcher")
    logger.info("=" * 60)
    
    fetcher = ClinicalTrialsFetcher()
    
    # Test search
    condition = "diabetes"
    trials = fetcher.search_and_fetch(condition=condition, max_results=5)
    
    if trials:
        logger.info(f"\n✅ Successfully fetched {len(trials)} trials")
        logger.info("\nFirst trial:")
        first = trials[0]
        logger.info(f"  NCT ID: {first['nct_id']}")
        logger.info(f"  Title: {first['title'][:100]}...")
        logger.info(f"  Status: {first['status']}")
        logger.info(f"  Phases: {', '.join(first['phases'])}")
        logger.info(f"  Conditions: {', '.join(first['conditions'][:3])}")
        logger.info(f"  Enrollment: {first['enrollment']}")
        
        # Save to storage
        storage = DataStorage()
        filepath = storage.save_clinical_trials(trials, condition)
        logger.info(f"\n💾 Saved to: {filepath}")
    else:
        logger.warning("❌ No trials found")


def main():
    """Run all tests."""
    try:
        test_pubmed()
        test_clinical_trials()
        
        logger.info("\n" + "=" * 60)
        logger.info("✨ All tests completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
