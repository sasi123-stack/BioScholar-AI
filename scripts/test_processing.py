"""Test script for data processing pipeline."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_pipeline import (
    PubMedFetcher,
    ClinicalTrialsFetcher,
    DataProcessor
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_processing():
    """Test complete data processing pipeline."""
    logger.info("=" * 60)
    logger.info("Testing Data Processing Pipeline")
    logger.info("=" * 60)
    
    processor = DataProcessor()
    
    # Test 1: Fetch and process PubMed articles
    logger.info("\n1. Testing PubMed article processing...")
    pubmed = PubMedFetcher()
    articles = pubmed.search_and_fetch("diabetes treatment", max_results=10)
    
    if articles:
        valid, invalid = processor.process_pubmed_articles(
            articles,
            validate=True,
            save=True,
            query="diabetes treatment"
        )
        
        logger.info(f"✅ Processed {len(valid)} valid articles")
        if invalid:
            logger.warning(f"⚠️  {len(invalid)} invalid articles")
        
        # Show sample normalized article
        if valid:
            sample = valid[0]
            logger.info("\nSample normalized article:")
            logger.info(f"  ID: {sample['id']}")
            logger.info(f"  Title: {sample['title'][:80]}...")
            logger.info(f"  Full text length: {len(sample['full_text'])} chars")
            logger.info(f"  Keywords: {', '.join(sample['keywords'][:5])}")
            logger.info(f"  Publication date: {sample['publication_date']}")
    
    # Test 2: Fetch and process clinical trials
    logger.info("\n2. Testing clinical trial processing...")
    trials_fetcher = ClinicalTrialsFetcher()
    trials = trials_fetcher.search_and_fetch(condition="cancer", max_results=10)
    
    if trials:
        valid, invalid = processor.process_clinical_trials(
            trials,
            validate=True,
            save=True,
            query="cancer"
        )
        
        logger.info(f"✅ Processed {len(valid)} valid trials")
        if invalid:
            logger.warning(f"⚠️  {len(invalid)} invalid trials")
        
        # Show sample normalized trial
        if valid:
            sample = valid[0]
            logger.info("\nSample normalized trial:")
            logger.info(f"  ID: {sample['id']}")
            logger.info(f"  Title: {sample['title'][:80]}...")
            logger.info(f"  Full text length: {len(sample['full_text'])} chars")
            logger.info(f"  Conditions: {', '.join(sample['conditions'][:3])}")
            logger.info(f"  Status: {sample['status']}")
            logger.info(f"  Phases: {', '.join(sample['phases'])}")
    
    logger.info("\n" + "=" * 60)
    logger.info("✨ Processing pipeline test complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        test_processing()
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        sys.exit(1)
