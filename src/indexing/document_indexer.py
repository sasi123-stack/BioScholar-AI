"""Document indexing for Elasticsearch."""

import traceback
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
        """Index a single document."""
        try:
            if doc_id is None:
                doc_id = document.get('id')
            
            if not doc_id:
                logger.error("Document must have an ID")
                return False
            
            client = self.es_client.client
            
            # Universal indexing approach:
            # Try keyword 'document' (ES 8.x), then 'body' (ES < 8 or OpenSearch)
            try:
                # Attempt newer ES style
                client.index(index=index_name, id=doc_id, document=document)
                return True
            except TypeError:
                # Fallback to body (OpenSearch / older ES)
                try:
                    client.index(index=index_name, id=doc_id, body=document)
                    return True
                except Exception as inner_e:
                    logger.error(f"Fallback indexing failed for document {doc_id}: {inner_e}")
                    raise
            except Exception as e:
                # If it's not a TypeError, pass it up to catch logic rejection (like 400 Bad Request)
                raise e
            
        except Exception as e:
            logger.error(f"Failed to index document {doc_id}: {e}")
            # Log full traceback for debugging mapping errors
            if "RequestError" in str(e) or "400" in str(e):
                logger.debug(traceback.format_exc())
            return False
    
    def index_batch(
        self,
        index_name: str,
        documents: List[Dict],
        batch_size: int = 500
    ) -> tuple[int, int]:
        """Index a batch of documents using bulk API."""
        if not documents:
            logger.warning("No documents to index")
            return 0, 0
        
        try:
            # Prepare bulk actions
            actions = []
            for doc in documents:
                doc_id = doc.get('id')
                if not doc_id:
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
                
            return success_count, failed_count
            
        except Exception as e:
            logger.error(f"Failed to index batch: {e}")
            raise
    
    def update_document(self, index_name: str, doc_id: str, updates: Dict) -> bool:
        """Update a document."""
        try:
            # update still uses body usually
            self.es_client.client.update(
                index=index_name,
                id=doc_id,
                body={'doc': updates}
            )
            return True
        except Exception as e:
            logger.error(f"Failed to update document {doc_id}: {e}")
            return False
    
    def delete_document(self, index_name: str, doc_id: str) -> bool:
        """Delete a document."""
        try:
            self.es_client.client.delete(index=index_name, id=doc_id)
            return True
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False
    
    def get_document(self, index_name: str, doc_id: str) -> Optional[Dict]:
        """Get a document by ID."""
        try:
            result = self.es_client.client.get(index=index_name, id=doc_id)
            return result['_source']
        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")
            return None
    
    def document_exists(self, index_name: str, doc_id: str) -> bool:
        """Check if a document exists."""
        try:
            return self.es_client.client.exists(index=index_name, id=doc_id)
        except:
            return False
