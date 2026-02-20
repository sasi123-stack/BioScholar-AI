"""Data storage utilities for saving fetched articles and trials."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from src.utils.config import PROJECT_ROOT
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataStorage:
    """Handles storage of fetched data to disk."""
    
    def __init__(self, data_dir: Path = None):
        """Initialize data storage.
        
        Args:
            data_dir: Base directory for data storage
        """
        self.data_dir = data_dir or PROJECT_ROOT / "data"
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        
        # Create directories
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Data storage initialized at: {self.data_dir}")
    
    def save_pubmed_articles(
        self,
        articles: List[Dict],
        query: str,
        filename: str = None
    ) -> Path:
        """Save PubMed articles to JSON file.
        
        Args:
            articles: List of article dictionaries
            query: Search query used
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_query = "".join(c if c.isalnum() else "_" for c in query[:30])
            filename = f"pubmed_{safe_query}_{timestamp}.json"
        
        filepath = self.raw_dir / "pubmed" / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "count": len(articles),
            "articles": articles
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(articles)} PubMed articles to: {filepath}")
        return filepath
    
    def save_clinical_trials(
        self,
        trials: List[Dict],
        query: str = None,
        filename: str = None
    ) -> Path:
        """Save clinical trials to JSON file.
        
        Args:
            trials: List of trial dictionaries
            query: Search query used
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if query:
                safe_query = "".join(c if c.isalnum() else "_" for c in query[:30])
                filename = f"trials_{safe_query}_{timestamp}.json"
            else:
                filename = f"trials_{timestamp}.json"
        
        filepath = self.raw_dir / "clinical_trials" / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "count": len(trials),
            "trials": trials
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(trials)} clinical trials to: {filepath}")
        return filepath
    
    def load_pubmed_articles(self, filename: str) -> List[Dict]:
        """Load PubMed articles from JSON file.
        
        Args:
            filename: Name of file to load
            
        Returns:
            List of article dictionaries
        """
        filepath = self.raw_dir / "pubmed" / filename
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        articles = data.get("articles", [])
        logger.info(f"Loaded {len(articles)} PubMed articles from: {filepath}")
        return articles
    
    def load_clinical_trials(self, filename: str) -> List[Dict]:
        """Load clinical trials from JSON file.
        
        Args:
            filename: Name of file to load
            
        Returns:
            List of trial dictionaries
        """
        filepath = self.raw_dir / "clinical_trials" / filename
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        trials = data.get("trials", [])
        logger.info(f"Loaded {len(trials)} clinical trials from: {filepath}")
        return trials
    
    def list_pubmed_files(self) -> List[str]:
        """List all saved PubMed data files.
        
        Returns:
            List of filenames
        """
        pubmed_dir = self.raw_dir / "pubmed"
        if not pubmed_dir.exists():
            return []
        
        files = [f.name for f in pubmed_dir.glob("*.json")]
        return sorted(files)
    
    def list_clinical_trials_files(self) -> List[str]:
        """List all saved clinical trials data files.
        
        Returns:
            List of filenames
        """
        trials_dir = self.raw_dir / "clinical_trials"
        if not trials_dir.exists():
            return []
        
        files = [f.name for f in trials_dir.glob("*.json")]
        return sorted(files)
