"""Hybrid search combining BM25 and semantic search."""

import numpy as np
from typing import List, Dict, Optional, Tuple
from elasticsearch import Elasticsearch

from src.utils.logger import get_logger
from src.indexing import ElasticsearchClient
from src.nlp_engine import EmbeddingGenerator
from .query_processor import QueryProcessor

logger = get_logger(__name__)


class HybridSearchEngine:
    """Hybrid search engine combining keyword (BM25) and semantic search."""
    
    def __init__(
        self,
        es_client: Optional[ElasticsearchClient] = None,
        embedding_generator: Optional[EmbeddingGenerator] = None,
        query_processor: Optional[QueryProcessor] = None,
        alpha: float = 0.5
    ):
        """Initialize hybrid search engine.
        
        Args:
            es_client: Elasticsearch client
            embedding_generator: Embedding generator for semantic search
            query_processor: Query processor for query enhancement
            alpha: Weight for BM25 score (1-alpha for semantic score)
        """
        self.es_client = es_client or ElasticsearchClient()
        self.embedding_generator = embedding_generator or EmbeddingGenerator(model_type="biobert")
        self.query_processor = query_processor or QueryProcessor()
        self.alpha = alpha
        
        logger.info(f"HybridSearchEngine initialized with alpha={alpha}")
    
    def keyword_search(
        self,
        index_name: str,
        query: str,
        size: int = 100,
        fields: Optional[List[str]] = None,
        date_from: Optional[int] = None,
        date_to: Optional[int] = None,
        article_types: Optional[List[str]] = None,
        subject: Optional[str] = None,
        availability: Optional[str] = None,
        sort_by: str = "relevance"
    ) -> List[Dict]:
        """Perform keyword-based search (BM25).
        
        Args:
            index_name: Index to search
            query: Search query
            size: Number of results to return
            fields: Fields to search
            date_from: Start year
            date_to: End year
            article_types: Article types filter
            subject: Subject filter
            availability: Availability filter
            sort_by: Sort criteria
            
        Returns:
            List of search results with scores
        """
        # Build Elasticsearch query
        es_query = self.query_processor.build_elasticsearch_query(
            query, fields, date_from=date_from, date_to=date_to,
            article_types=article_types, subject=subject, availability=availability
        )
        es_query['size'] = size
        
        # Add sorting
        if sort_by == "date_desc":
            es_query['sort'] = [
                {"publication_year": {"order": "desc", "unmapped_type": "integer"}},
                {"year": {"order": "desc", "unmapped_type": "integer"}},
                "_score"
            ]
        elif sort_by == "date_asc":
            es_query['sort'] = [
                {"publication_year": {"order": "asc", "unmapped_type": "integer"}},
                {"year": {"order": "asc", "unmapped_type": "integer"}},
                "_score"
            ]
        
        logger.debug(f"Keyword search query: {es_query}")
        
        # Execute search
        response = self.es_client.client.search(
            index=index_name,
            body=es_query
        )
        
        # Extract results
        results = []
        for hit in response['hits']['hits']:
            result = {
                'id': hit['_id'],
                'score': hit['_score'],
                'source': hit['_source']
            }
            results.append(result)
        
        logger.info(f"Keyword search returned {len(results)} results")
        
        return results
    
    def semantic_search(
        self,
        index_name: str,
        query: str,
        size: int = 100,
        embedding_field: str = 'embedding',
        date_from: Optional[int] = None,
        date_to: Optional[int] = None,
        article_types: Optional[List[str]] = None,
        subject: Optional[str] = None,
        availability: Optional[str] = None,
        sort_by: str = "relevance"
    ) -> List[Dict]:
        """Perform semantic search using embeddings.
        
        Args:
            index_name: Index to search
            query: Search query
            size: Number of results to return
            embedding_field: Name of embedding field in documents
            date_from: Start year
            date_to: End year
            article_types: Article types filter
            subject: Subject filter
            availability: Availability filter
            sort_by: Sort criteria
            
        Returns:
            List of search results with similarity scores
        """
        # Generate query embedding
        query_embedding = self.embedding_generator.encode_text(query)[0]
        
        # Build filter clause
        filter_clauses = []
        if date_from or date_to:
            range_filter = {}
            if date_from:
                range_filter['gte'] = str(date_from)
            if date_to:
                range_filter['lte'] = str(date_to)
            
            filter_clauses.append({
                "bool": {
                    "should": [
                        {"range": {"publication_year.keyword": range_filter}},
                        {"range": {"year.keyword": range_filter}},
                        {"range": {"start_year.keyword": range_filter}},
                        {"range": {"metadata.publication_year.keyword": range_filter}},
                        {"range": {"metadata.year.keyword": range_filter}}
                    ],
                    "minimum_should_match": 1
                }
            })

        # Article Type Filter
        if article_types and len(article_types) > 0:
            filter_clauses.append({
                "terms": {
                    "metadata.article_type.keyword": article_types
                }
            })
            
        # Subject Filter
        if subject and subject != 'all':
            filter_clauses.append({
                "term": {
                    "metadata.subject.keyword": subject
                }
            })
            
        # Availability Filter
        if availability and availability != 'all':
            if availability == 'full_text':
                filter_clauses.append({
                    "exists": {
                        "field": "full_text"
                    }
                })
            elif availability == 'open_access':
                 filter_clauses.append({
                    "term": {
                        "metadata.is_open_access": True
                    }
                })

        # Build cosine similarity query
        base_query = {'match_all': {}}
        if filter_clauses:
            base_query = {
                'bool': {
                    'filter': filter_clauses
                }
            }

        # Build script for vector similarity
        # ES uses cosineSimilarity, OpenSearch requires manual dot product in Painless
        is_opensearch = getattr(self.es_client, '_is_opensearch', False)
        
        if is_opensearch:
            # Manual dot product for OpenSearch compatibility
            script_source = (
                f"double dot = 0; "
                f"if (doc.containsKey('{embedding_field}') && doc['{embedding_field}'].size() > 0) {{ "
                f"  for (int i = 0; i < params.query_vector.length; i++) {{ "
                f"    dot += (double)params.query_vector[i] * (double)doc['{embedding_field}'][i]; "
                f"  }} "
                f"}} "
                f"return dot + 1.0;"
            )
        else:
            # Standard Elasticsearch cosine similarity
            script_source = f"cosineSimilarity(params.query_vector, '{embedding_field}') + 1.0"

        es_query = {
            'size': size,
            'query': {
                'script_score': {
                    'query': base_query,
                    'script': {
                        'source': script_source,
                        'params': {
                            'query_vector': query_embedding.tolist()
                        }
                    }
                }
            }
        }
        
        # Add sorting - only if we want to override similarity
        if sort_by == "date_desc":
            es_query['sort'] = [
                {"publication_year": {"order": "desc", "unmapped_type": "integer"}},
                {"year": {"order": "desc", "unmapped_type": "integer"}},
                "_score"
            ]
        elif sort_by == "date_asc":
            es_query['sort'] = [
                {"publication_year": {"order": "asc", "unmapped_type": "integer"}},
                {"year": {"order": "asc", "unmapped_type": "integer"}},
                "_score"
            ]
            
        logger.debug(f"Semantic search for: {query}")
        
        # Execute search
        try:
            response = self.es_client.client.search(
                index=index_name,
                body=es_query
            )
            
            # Extract results
            results = []
            for hit in response['hits']['hits']:
                result = {
                    'id': hit['_id'],
                    'score': hit['_score'] - 1.0 if '_score' in hit else 0.0,
                    'source': hit['_source']
                }
                results.append(result)
            
            logger.info(f"Semantic search returned {len(results)} results")
            
            return results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            # If semantic search fails (e.g. no embedding field), return empty list
            # The hybrid search aggregator will then just use keyword results
            return []
    
    def hybrid_search(
        self,
        index_name: str,
        query: str,
        size: int = 20,
        alpha: Optional[float] = None,
        date_from: Optional[int] = None,
        date_to: Optional[int] = None,
        article_types: Optional[List[str]] = None,
        subject: Optional[str] = None,
        availability: Optional[str] = None,
        sort_by: str = "relevance"
    ) -> List[Dict]:
        """Perform hybrid search combining BM25 and semantic search.
        
        Args:
            index_name: Index to search (or 'all' for all indices)
            query: Search query
            size: Number of results to return
            alpha: Weight for BM25 score (overrides default)
            date_from: Start year
            date_to: End year
            article_types: Article types filter
            subject: Subject filter
            availability: Availability filter
            sort_by: Sort criteria
            
        Returns:
            List of search results with combined scores
        """
        alpha = alpha if alpha is not None else self.alpha
        
        logger.info(f"Hybrid search: '{query}' (alpha={alpha}, sort={sort_by})")
        
        # Handle 'all' index - search both indices
        if index_name == 'all':
            index_name = 'pubmed_articles,clinical_trials'
        
        # Process query
        processed = self.query_processor.process_query(query)
        expanded_query = processed['expanded']
        
        # Perform both searches with date filters
        # Note: we use relevance sorting for the sub-searches to get top relevant candidates
        keyword_results = self.keyword_search(
            index_name, expanded_query, size=size*2, 
            date_from=date_from, date_to=date_to, 
            article_types=article_types, subject=subject, availability=availability,
            sort_by="relevance"
        )
        semantic_results = self.semantic_search(
            index_name, query, size=size*2, 
            date_from=date_from, date_to=date_to,
            article_types=article_types, subject=subject, availability=availability, 
            sort_by="relevance"
        )
        
        # Normalize scores
        keyword_scores = self._normalize_scores([r['score'] for r in keyword_results])
        semantic_scores = self._normalize_scores([r['score'] for r in semantic_results])
        
        # Create score dictionaries
        kw_score_dict = {r['id']: score for r, score in zip(keyword_results, keyword_scores)}
        sem_score_dict = {r['id']: score for r, score in zip(semantic_results, semantic_scores)}
        
        # Combine results
        all_ids = set(kw_score_dict.keys()) | set(sem_score_dict.keys())
        
        combined_results = []
        for doc_id in all_ids:
            kw_score = kw_score_dict.get(doc_id, 0.0)
            sem_score = sem_score_dict.get(doc_id, 0.0)
            
            # Weighted combination
            combined_score = alpha * kw_score + (1 - alpha) * sem_score
            
            # Get document source (prefer keyword results)
            source = None
            for r in keyword_results:
                if r['id'] == doc_id:
                    source = r['source']
                    break
            if source is None:
                for r in semantic_results:
                    if r['id'] == doc_id:
                        source = r['source']
                        break
            
            if source:
                combined_results.append({
                    'id': doc_id,
                    'score': combined_score,
                    'keyword_score': kw_score,
                    'semantic_score': sem_score,
                    'source': source
                })
        
        # Sort by combined score or date
        if sort_by == "date_desc":
            combined_results.sort(
                key=lambda x: (
                    x['source'].get('publication_year') or x['source'].get('year') or 0,
                    x['score']
                ), 
                reverse=True
            )
        elif sort_by == "date_asc":
            combined_results.sort(
                key=lambda x: (
                    x['source'].get('publication_year') or x['source'].get('year') or 9999,
                    -x['score']
                )
            )
        else:
            combined_results.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top results
        final_results = combined_results[:size]
        
        logger.info(f"Hybrid search returned {len(final_results)} results")
        
        return final_results
    
    def _normalize_scores(self, scores: List[float]) -> List[float]:
        """Normalize scores to [0, 1] range using min-max normalization.
        
        Args:
            scores: List of scores
            
        Returns:
            Normalized scores
        """
        if not scores or len(scores) == 1:
            return [1.0] * len(scores)
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score == min_score:
            return [1.0] * len(scores)
        
        normalized = [(s - min_score) / (max_score - min_score) for s in scores]
        
        return normalized
    
    def search_pubmed(self, query: str, size: int = 20, **kwargs) -> List[Dict]:
        """Search PubMed articles.
        
        Args:
            query: Search query
            size: Number of results
            **kwargs: Additional search parameters
            
        Returns:
            List of search results
        """
        return self.hybrid_search('pubmed_articles', query, size, **kwargs)
    
    def search_clinical_trials(self, query: str, size: int = 20, **kwargs) -> List[Dict]:
        """Search clinical trials.
        
        Args:
            query: Search query
            size: Number of results
            **kwargs: Additional search parameters
            
        Returns:
            List of search results
        """
        return self.hybrid_search('clinical_trials', query, size, **kwargs)
    
    def search_all(self, query: str, size: int = 20, **kwargs) -> Dict[str, List[Dict]]:
        """Search across all indices.
        
        Args:
            query: Search query
            size: Number of results per index
            **kwargs: Additional search parameters
            
        Returns:
            Dictionary with results per index
        """
        results = {
            'pubmed': self.search_pubmed(query, size, **kwargs),
            'clinical_trials': self.search_clinical_trials(query, size, **kwargs)
        }
        
        return results
    
    def close(self):
        """Close connections."""
        if self.es_client:
            self.es_client.close()
