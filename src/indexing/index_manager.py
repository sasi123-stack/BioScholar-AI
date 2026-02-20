"""Index management for Elasticsearch."""

from typing import Dict, List, Optional

from src.utils.logger import get_logger
from .es_client import ElasticsearchClient

logger = get_logger(__name__)


class IndexManager:
    """Manages Elasticsearch indices."""
    
    # Index settings for biomedical text
    PUBMED_INDEX_SETTINGS = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "analyzer": {
                    "biomedical_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "stop",
                            "snowball"
                        ]
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "source": {"type": "keyword"},
                "type": {"type": "keyword"},
                "title": {
                    "type": "text",
                    "analyzer": "biomedical_analyzer",
                    "fields": {
                        "keyword": {"type": "keyword"}
                    }
                },
                "abstract": {
                    "type": "text",
                    "analyzer": "biomedical_analyzer"
                },
                "full_text": {
                    "type": "text",
                    "analyzer": "biomedical_analyzer"
                },
                "authors": {"type": "text"},
                "journal": {
                    "type": "text",
                    "fields": {
                        "keyword": {"type": "keyword"}
                    }
                },
                "publication_year": {"type": "keyword"},
                "publication_month": {"type": "keyword"},
                "publication_date": {"type": "keyword"},
                "mesh_terms": {"type": "keyword"},
                "keywords": {"type": "keyword"},
                "doi": {"type": "keyword"},
                "metadata": {"type": "object"},
                "embedding": {
                    "type": "dense_vector",
                    "dims": 768,
                    "index": True,
                    "similarity": "cosine"
                }
            }
        }
    }
    
    CLINICAL_TRIALS_INDEX_SETTINGS = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "analyzer": {
                    "biomedical_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "stop",
                            "snowball"
                        ]
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "source": {"type": "keyword"},
                "type": {"type": "keyword"},
                "title": {
                    "type": "text",
                    "analyzer": "biomedical_analyzer",
                    "fields": {
                        "keyword": {"type": "keyword"}
                    }
                },
                "abstract": {
                    "type": "text",
                    "analyzer": "biomedical_analyzer"
                },
                "full_text": {
                    "type": "text",
                    "analyzer": "biomedical_analyzer"
                },
                "conditions": {"type": "keyword"},
                "interventions": {"type": "object"},
                "primary_outcomes": {"type": "text"},
                "secondary_outcomes": {"type": "text"},
                "phases": {"type": "keyword"},
                "status": {"type": "keyword"},
                "enrollment": {"type": "integer"},
                "start_date": {"type": "keyword"},
                "completion_date": {"type": "keyword"},
                "publication_year": {"type": "keyword"},
                "sponsor": {
                    "type": "text",
                    "fields": {
                        "keyword": {"type": "keyword"}
                    }
                },
                "locations": {"type": "text"},
                "keywords": {"type": "keyword"},
                "metadata": {"type": "object"},
                "embedding": {
                    "type": "dense_vector",
                    "dims": 768,
                    "index": True,
                    "similarity": "cosine"
                }
            }
        }
    }
    
    def __init__(self, es_client: ElasticsearchClient):
        """Initialize index manager.
        
        Args:
            es_client: Elasticsearch client instance
        """
        self.es_client = es_client
    
    def create_index(
        self,
        index_name: str,
        settings: Optional[Dict] = None,
        force: bool = False
    ) -> bool:
        """Create an index.
        
        Args:
            index_name: Name of the index to create
            settings: Index settings and mappings
            force: If True, delete existing index first
            
        Returns:
            True if created successfully
        """
        try:
            # Check if index exists
            if self.es_client.client.indices.exists(index=index_name):
                if force:
                    logger.info(f"Deleting existing index: {index_name}")
                    self.es_client.client.indices.delete(index=index_name)
                else:
                    logger.warning(f"Index already exists: {index_name}")
                    return False
            
            # Create index
            if settings is None:
                settings = self._get_default_settings(index_name)
            
            self.es_client.client.indices.create(
                index=index_name,
                body=settings
            )
            
            logger.info(f"Created index: {index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create index {index_name}: {e}")
            raise
    
    def delete_index(self, index_name: str) -> bool:
        """Delete an index.
        
        Args:
            index_name: Name of the index to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            if not self.es_client.client.indices.exists(index=index_name):
                logger.warning(f"Index does not exist: {index_name}")
                return False
            
            self.es_client.client.indices.delete(index=index_name)
            logger.info(f"Deleted index: {index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete index {index_name}: {e}")
            raise
    
    def index_exists(self, index_name: str) -> bool:
        """Check if an index exists.
        
        Args:
            index_name: Name of the index
            
        Returns:
            True if exists
        """
        return self.es_client.client.indices.exists(index=index_name)
    
    def get_index_info(self, index_name: str) -> Dict:
        """Get index information.
        
        Args:
            index_name: Name of the index
            
        Returns:
            Index information dictionary
        """
        try:
            return self.es_client.client.indices.get(index=index_name)
        except Exception as e:
            logger.error(f"Failed to get index info for {index_name}: {e}")
            raise
    
    def get_document_count(self, index_name: str) -> int:
        """Get document count in index.
        
        Args:
            index_name: Name of the index
            
        Returns:
            Number of documents
        """
        try:
            result = self.es_client.client.count(index=index_name)
            return result['count']
        except Exception as e:
            logger.error(f"Failed to get document count for {index_name}: {e}")
            return 0
    
    def list_indices(self) -> List[str]:
        """List all indices.
        
        Returns:
            List of index names
        """
        try:
            indices = self.es_client.client.indices.get_alias(index="*")
            return list(indices.keys())
        except Exception as e:
            logger.error(f"Failed to list indices: {e}")
            return []
    
    def refresh_index(self, index_name: str):
        """Refresh an index to make recent changes searchable.
        
        Args:
            index_name: Name of the index to refresh
        """
        try:
            self.es_client.client.indices.refresh(index=index_name)
            logger.debug(f"Refreshed index: {index_name}")
        except Exception as e:
            logger.error(f"Failed to refresh index {index_name}: {e}")
    
    def _get_default_settings(self, index_name: str) -> Dict:
        """Get default settings for an index based on name.
        
        Args:
            index_name: Name of the index
            
        Returns:
            Settings dictionary
        """
        if "pubmed" in index_name.lower():
            return self.PUBMED_INDEX_SETTINGS
        elif "trial" in index_name.lower() or "clinical" in index_name.lower():
            return self.CLINICAL_TRIALS_INDEX_SETTINGS
        else:
            # Generic settings
            return {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                }
            }
    
    def setup_default_indices(self, force: bool = False):
        """Setup default PubMed and Clinical Trials indices.
        
        Args:
            force: If True, recreate existing indices
        """
        logger.info("Setting up default indices...")
        
        # Create PubMed index
        self.create_index(
            "pubmed_articles",
            self.PUBMED_INDEX_SETTINGS,
            force=force
        )
        
        # Create Clinical Trials index
        self.create_index(
            "clinical_trials",
            self.CLINICAL_TRIALS_INDEX_SETTINGS,
            force=force
        )
        
        logger.info("Default indices setup complete")
