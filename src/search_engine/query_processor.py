"""Query processing and enhancement."""

import re
from typing import List, Dict, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class QueryProcessor:
    """Process and enhance search queries."""
    
    def __init__(self):
        """Initialize query processor."""
        # Medical abbreviations and expansions
        self.medical_expansions = {
            'covid': 'COVID-19 coronavirus SARS-CoV-2',
            'covid-19': 'COVID-19 coronavirus SARS-CoV-2',
            'dm': 'diabetes mellitus',
            'htn': 'hypertension high blood pressure',
            'mi': 'myocardial infarction heart attack',
            'copd': 'chronic obstructive pulmonary disease',
            'ckd': 'chronic kidney disease',
            'cad': 'coronary artery disease',
            'chf': 'congestive heart failure',
            'uti': 'urinary tract infection',
            'tb': 'tuberculosis',
            'hiv': 'human immunodeficiency virus',
            'aids': 'acquired immunodeficiency syndrome',
            'copd': 'chronic obstructive pulmonary disease',
        }
        
        # Common stopwords (minimal for medical queries)
        self.stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
    
    def clean_query(self, query: str) -> str:
        """Clean and normalize query text.
        
        Args:
            query: Raw query string
            
        Returns:
            Cleaned query
        """
        # Convert to lowercase
        query = query.lower().strip()
        
        # Remove special characters but keep hyphens and apostrophes
        query = re.sub(r'[^\w\s\-\']', ' ', query)
        
        # Normalize whitespace
        query = re.sub(r'\s+', ' ', query)
        
        return query
    
    def expand_query(self, query: str) -> str:
        """Expand medical abbreviations in query.
        
        Args:
            query: Input query
            
        Returns:
            Expanded query
        """
        cleaned = self.clean_query(query)
        words = cleaned.split()
        
        expanded_parts = []
        for word in words:
            # Check if word is a known abbreviation
            if word in self.medical_expansions:
                expanded_parts.append(self.medical_expansions[word])
            else:
                expanded_parts.append(word)
        
        expanded = ' '.join(expanded_parts)
        logger.debug(f"Query expansion: '{query}' -> '{expanded}'")
        
        return expanded
    
    def extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query.
        
        Args:
            query: Input query
            
        Returns:
            List of keywords
        """
        cleaned = self.clean_query(query)
        words = cleaned.split()
        
        # Remove stopwords
        keywords = [w for w in words if w not in self.stopwords and len(w) > 2]
        
        return keywords
    
    def suggest_corrections(self, query: str) -> List[str]:
        """Suggest query corrections (basic implementation).
        
        Args:
            query: Input query
            
        Returns:
            List of suggested corrections
        """
        # This is a placeholder - in production, use a proper spell checker
        # or medical terminology dictionary
        suggestions = []
        
        cleaned = self.clean_query(query)
        
        # Check for common misspellings
        misspellings = {
            'diabetis': 'diabetes',
            'cancor': 'cancer',
            'inflamation': 'inflammation',
            'treatmnt': 'treatment',
            'medicin': 'medicine',
        }
        
        for wrong, correct in misspellings.items():
            if wrong in cleaned:
                corrected = cleaned.replace(wrong, correct)
                suggestions.append(corrected)
        
        return suggestions
    
    def build_elasticsearch_query(
        self,
        query: str,
        fields: Optional[List[str]] = None,
        boost_title: float = 2.0,
        date_from: Optional[int] = None,
        date_to: Optional[int] = None,
        article_types: Optional[List[str]] = None,
        subject: Optional[str] = None,
        availability: Optional[str] = None
    ) -> Dict:
        """Build Elasticsearch query DSL with optional filters.
        
        Args:
            query: Search query
            fields: Fields to search
            boost_title: Boost factor for title field
            date_from: Start year
            date_to: End year
            article_types: List of article types to include
            subject: Subject filter (human, animal, etc.)
            availability: Availability filter (full_text, free, etc.)
            
        Returns:
            Elasticsearch query dictionary
        """
        if fields is None:
            fields = ['title', 'abstract', 'keywords']
        
        # Expand query
        expanded_query = self.expand_query(query)
        
        # Build multi-match query
        must_match = {
            'bool': {
                'should': [
                    {
                        'multi_match': {
                            'query': expanded_query,
                            'fields': [
                                f'title^{boost_title}',
                                'abstract',
                                'keywords^1.5',
                                'full_text'
                            ],
                            'type': 'best_fields',
                            'operator': 'or',
                            'fuzziness': 'AUTO'
                        }
                    },
                    {
                        'match_phrase': {
                            'title': {
                                'query': query,
                                'boost': boost_title * 1.5
                            }
                        }
                    }
                ],
                'minimum_should_match': 1
            }
        }

        # Build filter clause
        filter_clauses = []
        
        # Date Filter
        if date_from or date_to:
            range_filter = {}
            if date_from:
                range_filter['gte'] = str(date_from)
            if date_to:
                range_filter['lte'] = str(date_to)
            
            # Target both potential year fields
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
            # Map frontend types to potential backend values if needed
            # For now assume direct mapping to metadata.article_type
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

        es_query = {
            'query': {
                'bool': {
                    'must': [must_match]
                }
            }
        }
        
        if filter_clauses:
            es_query['query']['bool']['filter'] = filter_clauses
            
        return es_query
    
    def process_query(self, query: str) -> Dict:
        """Process query and return enhanced version with metadata.
        
        Args:
            query: Input query
            
        Returns:
            Dictionary with processed query information
        """
        cleaned = self.clean_query(query)
        expanded = self.expand_query(query)
        keywords = self.extract_keywords(query)
        suggestions = self.suggest_corrections(query)
        
        result = {
            'original': query,
            'cleaned': cleaned,
            'expanded': expanded,
            'keywords': keywords,
            'suggestions': suggestions
        }
        
        logger.debug(f"Processed query: {result}")
        
        return result
