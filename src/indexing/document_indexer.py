"""Document indexing for Elasticsearch."""

from typing import Dict, List, Optional

from elasticsearch import helpers

from src.utils.logger import get_logger
from .es_client import ElasticsearchClient

logger = get_logger(__name__)


class DocumentIndexer:
    """Indexes documents into Elasticsearch."""
    
    def __init__(self, es_client: ElasticsearchClient):
        """Initialize document indexer.
        
        Args:
            es_client: Elasticsearch client instance
        """
        self.es_client = es_client
    
    def index_document(
        self,
        index_name: str,
        document: Dict,
        doc_id: Optional[str] = None
    ) -> bool:
        """Index a single document.
        
        Args:
            index_name: Name of the index
            document: Document to index
            doc_id: Optional document ID (uses document['id'] if not provided)
            
        Returns:
            True if indexed successfully
        """
        try:
            if doc_id is None:
                doc_id = document.get('id')
            
            if not doc_id:
                logger.error("Document must have an ID")
                return False
            
            self.es_client.client.index(
                index=index_name,
                id=doc_id,
                document=document
            )
            
            logger.debug(f"Indexed document {doc_id} to {index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index document {doc_id}: {e}")
            return False
    
    def index_batch(
        self,
        index_name: str,
        documents: List[Dict],
        batch_size: int = 500
    ) -> tuple[int, int]:
        """Index a batch of documents using bulk API.
        
        Args:
            index_name: Name of the index
            documents: List of documents to index
            batch_size: Number of documents per batch
            
        Returns:
            Tuple of (successful_count, failed_count)
        """
        if not documents:
            logger.warning("No documents to index")
            return 0, 0
        
        try:
            # Prepare bulk actions
            actions = []
            for doc in documents:
                doc_id = doc.get('id')
                if not doc_id:
                    logger.warning("Skipping document without ID")
                    continue
                
                action = {
                    '_index': index_name,
                    '_id': doc_id,
                    '_source': doc
                }
                actions.append(action)
            
            # Execute bulk indexing
            success_count = 0
            failed_count = 0
            
            for i in range(0, len(actions), batch_size):
                batch = actions[i:i + batch_size]
                
                success, failed = helpers.bulk(
                    self.es_client.client,
                    batch,
                    stats_only=True,
                    raise_on_error=False
                )
                
                success_count += success
                failed_count += len(batch) - success
                
                logger.info(
                    f"Indexed batch {i//batch_size + 1}: "
                    f"{success} successful, {len(batch) - success} failed"
                )
            
            logger.info(
                f"Batch indexing complete: {success_count} successful, "
                f"{failed_count} failed"
            )
            
            return success_count, failed_count
            
        except Exception as e:
            logger.error(f"Failed to index batch: {e}")
            raise
    
    def update_document(
        self,
        index_name: str,
        doc_id: str,
        updates: Dict
    ) -> bool:
        """Update a document.
        
        Args:
            index_name: Name of the index
            doc_id: Document ID
            updates: Fields to update
            
        Returns:
            True if updated successfully
        """
        try:
            self.es_client.client.update(
                index=index_name,
                id=doc_id,
                body={'doc': updates}
            )
            
            logger.debug(f"Updated document {doc_id} in {index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document {doc_id}: {e}")
            return False
    
    def delete_document(
        self,
        index_name: str,
        doc_id: str
    ) -> bool:
        """Delete a document.
        
        Args:
            index_name: Name of the index
            doc_id: Document ID
            
        Returns:
            True if deleted successfully
        """
        try:
            self.es_client.client.delete(
                index=index_name,
                id=doc_id
            )
            
            logger.debug(f"Deleted document {doc_id} from {index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False
    
    def get_document(
        self,
        index_name: str,
        doc_id: str
    ) -> Optional[Dict]:
        """Get a document by ID.
        
        Args:
            index_name: Name of the index
            doc_id: Document ID
            
        Returns:
            Document dictionary or None if not found
        """
        try:
            result = self.es_client.client.get(
                index=index_name,
                id=doc_id
            )
            return result['_source']
            
        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")
            return None
    
    def document_exists(
        self,
        index_name: str,
        doc_id: str
    ) -> bool:
        """Check if a document exists.
        
        Args:
            index_name: Name of the index
            doc_id: Document ID
            
        Returns:
            True if exists
        """
        try:
            return self.es_client.client.exists(
                index=index_name,
                id=doc_id
            )
        except:
            return False
