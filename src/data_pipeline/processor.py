"""Complete data processing pipeline."""

from typing import Dict, List, Tuple

from .normalizer import DataNormalizer
from .validator import DataValidator
from .storage import DataStorage
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataProcessor:
    """End-to-end data processing pipeline."""
    
    def __init__(self):
        """Initialize data processor."""
        self.normalizer = DataNormalizer()
        self.validator = DataValidator()
        self.storage = DataStorage()
    
    def process_pubmed_articles(
        self,
        articles: List[Dict],
        validate: bool = True,
        save: bool = True,
        query: str = None
    ) -> Tuple[List[Dict], List[Dict]]:
        """Process PubMed articles through complete pipeline.
        
        Args:
            articles: List of raw article dictionaries
            validate: Whether to validate documents
            save: Whether to save processed data
            query: Original search query for metadata
            
        Returns:
            Tuple of (valid_processed_articles, invalid_articles)
        """
        logger.info(f"Processing {len(articles)} PubMed articles...")
        
        # Step 1: Normalize
        normalized = self.normalizer.normalize_batch_pubmed(articles)
        
        # Step 2: Validate
        if validate:
            valid, invalid = self.validator.validate_batch(
                normalized,
                doc_type="article"
            )
        else:
            valid = normalized
            invalid = []
        
        # Step 3: Save processed data
        if save and valid:
            filepath = self.storage.processed_dir / "pubmed"
            filepath.mkdir(parents=True, exist_ok=True)
            
            import json
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"processed_pubmed_{timestamp}.json"
            
            with open(filepath / filename, "w", encoding="utf-8") as f:
                json.dump({
                    "query": query,
                    "timestamp": datetime.now().isoformat(),
                    "count": len(valid),
                    "articles": valid
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(valid)} processed articles to: {filepath / filename}")
        
        logger.info(
            f"Processing complete: {len(valid)} valid, {len(invalid)} invalid"
        )
        
        return valid, invalid
    
    def process_clinical_trials(
        self,
        trials: List[Dict],
        validate: bool = True,
        save: bool = True,
        query: str = None
    ) -> Tuple[List[Dict], List[Dict]]:
        """Process clinical trials through complete pipeline.
        
        Args:
            trials: List of raw trial dictionaries
            validate: Whether to validate documents
            save: Whether to save processed data
            query: Original search query for metadata
            
        Returns:
            Tuple of (valid_processed_trials, invalid_trials)
        """
        logger.info(f"Processing {len(trials)} clinical trials...")
        
        # Step 1: Normalize
        normalized = self.normalizer.normalize_batch_trials(trials)
        
        # Step 2: Validate
        if validate:
            valid, invalid = self.validator.validate_batch(
                normalized,
                doc_type="trial"
            )
        else:
            valid = normalized
            invalid = []
        
        # Step 3: Save processed data
        if save and valid:
            filepath = self.storage.processed_dir / "clinical_trials"
            filepath.mkdir(parents=True, exist_ok=True)
            
            import json
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"processed_trials_{timestamp}.json"
            
            with open(filepath / filename, "w", encoding="utf-8") as f:
                json.dump({
                    "query": query,
                    "timestamp": datetime.now().isoformat(),
                    "count": len(valid),
                    "trials": valid
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(valid)} processed trials to: {filepath / filename}")
        
        logger.info(
            f"Processing complete: {len(valid)} valid, {len(invalid)} invalid"
        )
        
        return valid, invalid
