"""Text processor for biomedical documents."""

import re
from typing import List, Dict, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TextProcessor:
    """Process and prepare text for NLP models."""
    
    def __init__(self, max_chunk_size: int = 512):
        """Initialize text processor.
        
        Args:
            max_chunk_size: Maximum size for text chunks
        """
        self.max_chunk_size = max_chunk_size
    
    def prepare_for_embedding(
        self,
        text: str,
        max_length: int = 512
    ) -> str:
        """Prepare text for embedding generation.
        
        Args:
            text: Input text
            max_length: Maximum length (in characters, approximate)
            
        Returns:
            Processed text
        """
        if not text or not text.strip():
            return ""
        
        # Basic cleaning
        text = text.strip()
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Truncate if too long (rough approximation)
        if len(text) > max_length * 4:  # ~4 chars per token
            text = text[:max_length * 4]
        
        return text
    
    def chunk_text(
        self,
        text: str,
        chunk_size: Optional[int] = None,
        overlap: int = 50
    ) -> List[str]:
        """Split text into overlapping chunks.
        
        Args:
            text: Input text
            chunk_size: Size of each chunk (characters)
            overlap: Number of characters to overlap
            
        Returns:
            List of text chunks
        """
        chunk_size = chunk_size or self.max_chunk_size
        
        if not text or len(text) <= chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size // 2:  # Only break if not too early
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return chunks
    
    def extract_keywords(
        self,
        text: str,
        max_keywords: int = 10
    ) -> List[str]:
        """Extract potential keywords from text.
        
        Simple frequency-based extraction. For production, consider using
        more sophisticated methods like KeyBERT or RAKE.
        
        Args:
            text: Input text
            max_keywords: Maximum number of keywords
            
        Returns:
            List of keywords
        """
        if not text:
            return []
        
        # Simple tokenization
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Common stopwords
        stopwords = {
            'this', 'that', 'with', 'from', 'have', 'been', 'were',
            'they', 'their', 'there', 'these', 'those', 'will', 'would',
            'could', 'should', 'which', 'about', 'after', 'before'
        }
        
        # Filter and count
        word_counts = {}
        for word in words:
            if word not in stopwords:
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Sort by frequency
        keywords = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, _ in keywords[:max_keywords]]
    
    def combine_fields(
        self,
        document: Dict,
        fields: List[str],
        separator: str = " "
    ) -> str:
        """Combine multiple document fields into single text.
        
        Args:
            document: Document dictionary
            fields: List of field names to combine
            separator: Separator between fields
            
        Returns:
            Combined text
        """
        parts = []
        
        for field in fields:
            if field in document and document[field]:
                value = str(document[field])
                if value.strip():
                    parts.append(value.strip())
        
        return separator.join(parts)
    
    def prepare_document_for_indexing(
        self,
        document: Dict,
        text_fields: Optional[List[str]] = None
    ) -> Dict:
        """Prepare document for indexing by processing text fields.
        
        Args:
            document: Input document
            text_fields: Fields to process (default: ['title', 'abstract', 'full_text'])
            
        Returns:
            Processed document
        """
        if text_fields is None:
            text_fields = ['title', 'abstract', 'full_text']
        
        processed = document.copy()
        
        for field in text_fields:
            if field in processed and processed[field]:
                processed[field] = self.prepare_for_embedding(
                    str(processed[field])
                )
        
        return processed
