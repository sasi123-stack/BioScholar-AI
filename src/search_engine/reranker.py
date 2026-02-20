"""Cross-encoder reranker for improving search results."""

import torch
import numpy as np
from typing import List, Dict, Tuple
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from src.utils.logger import get_logger
from src.utils.config import settings

logger = get_logger(__name__)


class CrossEncoderReranker:
    """Rerank search results using a cross-encoder model."""
    
    def __init__(
        self,
        model_name: str = "dmis-lab/biobert-v1.1",
        device: str = None
    ):
        """Initialize cross-encoder reranker.
        
        Args:
            model_name: Name of cross-encoder model (default: dmis-lab/biobert-v1.1)
            device: Device to run model on ('cuda' or 'cpu')
        """
        self.model_name = model_name
        
        # Auto-detect device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        logger.info(f"Loading cross-encoder model: {model_name}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=settings.model_cache_dir
            )
            
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                cache_dir=settings.model_cache_dir
            )
            
            self.model = self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"✅ Cross-encoder loaded on {self.device}")
            
        except Exception as e:
            logger.warning(f"Failed to load cross-encoder: {e}")
            logger.warning("Reranking will be disabled")
            self.model = None
            self.tokenizer = None
    
    def score_pair(self, query: str, text: str) -> float:
        """Score a query-document pair.
        
        Args:
            query: Query text
            text: Document text
            
        Returns:
            Relevance score
        """
        if self.model is None:
            return 0.0
        
        # Tokenize
        inputs = self.tokenizer(
            query,
            text,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        
        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Get score
        with torch.no_grad():
            outputs = self.model(**inputs)
            score = outputs.logits[0][0].item()
        
        return score
    
    def score_batch(
        self,
        query: str,
        texts: List[str],
        batch_size: int = 8
    ) -> List[float]:
        """Score a batch of query-document pairs.
        
        Args:
            query: Query text
            texts: List of document texts
            batch_size: Batch size for processing
            
        Returns:
            List of relevance scores
        """
        if self.model is None:
            return [0.0] * len(texts)
        
        scores = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            # Create pairs
            pairs = [[query, text] for text in batch_texts]
            
            # Tokenize batch
            inputs = self.tokenizer(
                pairs,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get scores
            with torch.no_grad():
                outputs = self.model(**inputs)
                batch_scores = outputs.logits[:, 0].cpu().numpy().tolist()
            
            scores.extend(batch_scores)
        
        return scores
    
    def rerank(
        self,
        query: str,
        results: List[Dict],
        top_k: int = None,
        text_field: str = 'abstract'
    ) -> List[Dict]:
        """Rerank search results using cross-encoder.
        
        Args:
            query: Search query
            results: List of search results
            top_k: Number of top results to return (None = all)
            text_field: Field to use for reranking
            
        Returns:
            Reranked results
        """
        if self.model is None:
            logger.warning("Cross-encoder model not available, returning original results")
            return results[:top_k] if top_k else results
        
        if not results:
            return results
        
        logger.info(f"Reranking {len(results)} results")
        
        # Extract texts for reranking
        texts = []
        for result in results:
            source = result.get('source', {})
            
            # Combine title and text field
            title = source.get('title', '')
            text = source.get(text_field, '')
            combined = f"{title}. {text}".strip()
            
            texts.append(combined)
        
        # Score all pairs
        rerank_scores = self.score_batch(query, texts)
        
        # Add rerank scores to results
        reranked_results = []
        for result, rerank_score in zip(results, rerank_scores):
            result_copy = result.copy()
            result_copy['rerank_score'] = rerank_score
            # Combine original score with rerank score
            result_copy['final_score'] = result.get('score', 0.0) * 0.3 + rerank_score * 0.7
            reranked_results.append(result_copy)
        
        # Sort by final score
        reranked_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Return top k
        final_results = reranked_results[:top_k] if top_k else reranked_results
        
        logger.info(f"Reranking complete, returning {len(final_results)} results")
        
        return final_results
    
    def rerank_with_feedback(
        self,
        query: str,
        results: List[Dict],
        relevant_ids: List[str],
        top_k: int = None
    ) -> List[Dict]:
        """Rerank with relevance feedback.
        
        Args:
            query: Search query
            results: List of search results
            relevant_ids: List of IDs marked as relevant
            top_k: Number of top results to return
            
        Returns:
            Reranked results with feedback boost
        """
        # First perform standard reranking
        reranked = self.rerank(query, results, top_k=None)
        
        # Boost relevant documents
        for result in reranked:
            if result['id'] in relevant_ids:
                result['final_score'] = result.get('final_score', 0.0) * 1.5
        
        # Re-sort
        reranked.sort(key=lambda x: x['final_score'], reverse=True)
        
        return reranked[:top_k] if top_k else reranked
