"""Embedding generator for biomedical documents."""

import torch
import numpy as np
from typing import List, Union, Optional, Dict
from tqdm import tqdm

from src.utils.logger import get_logger
from .model_loader import ModelLoader

logger = get_logger(__name__)


class EmbeddingGenerator:
    """Generate embeddings using BioBERT or ClinicalBERT."""
    
    def __init__(
        self,
        model_type: str = "biobert",
        batch_size: int = 8,
        max_length: int = 512,
        model_loader: Optional[ModelLoader] = None
    ):
        """Initialize embedding generator.
        
        Args:
            model_type: Type of model ('biobert' or 'clinicalbert')
            batch_size: Batch size for processing
            max_length: Maximum sequence length
            model_loader: Optional ModelLoader instance
        """
        self.model_type = model_type.lower()
        self.batch_size = batch_size
        self.max_length = max_length
        
        # Initialize model loader but don't load models yet
        self.model_loader = model_loader or ModelLoader()
        self.model = None
        self.tokenizer = None
        
        self.device = self.model_loader.get_device()
        logger.info(f"EmbeddingGenerator initialized with {model_type} (lazy loading)")
    
    def _load_model(self):
        """Load the model if not already loaded."""
        if self.model is not None:
            return

        logger.info(f"Lazy loading {self.model_type} model...")
        if self.model_type == "biobert":
            self.model, self.tokenizer = self.model_loader.load_biobert()
        elif self.model_type == "clinicalbert":
            self.model, self.tokenizer = self.model_loader.load_clinicalbert()
        else:
            raise ValueError(f"Unknown model type: {self.model_type}. Use 'biobert' or 'clinicalbert'")
            
        logger.info(f"Model {self.model_type} loaded on {self.device}")

    def encode_text(
        self,
        text: Union[str, List[str]],
        show_progress: bool = False
    ) -> np.ndarray:
        """Encode text into embeddings.
        
        Args:
            text: Single text string or list of texts
            show_progress: Show progress bar for batch processing
            
        Returns:
            Numpy array of embeddings (shape: [n_texts, 768])
        """
        self._load_model()

        # Handle single text
        if isinstance(text, str):
            text = [text]
        
        all_embeddings = []
        
        # Process in batches
        iterator = range(0, len(text), self.batch_size)
        if show_progress:
            iterator = tqdm(iterator, desc=f"Generating {self.model_type} embeddings")
        
        with torch.no_grad():
            for i in iterator:
                batch_texts = text[i:i + self.batch_size]
                batch_embeddings = self._encode_batch(batch_texts)
                all_embeddings.append(batch_embeddings)
        
        # Concatenate all batches
        embeddings = np.vstack(all_embeddings)
        
        logger.debug(f"Generated embeddings shape: {embeddings.shape}")
        return embeddings
    
    def _encode_batch(self, texts: List[str]) -> np.ndarray:
        """Encode a batch of texts.
        
        Args:
            texts: List of texts
            
        Returns:
            Numpy array of embeddings
        """
        # Tokenize
        encoded = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt"
        )
        
        # Move to device
        encoded = {k: v.to(self.device) for k, v in encoded.items()}
        
        # Get embeddings
        outputs = self.model(**encoded)
        
        # Use [CLS] token embedding (first token)
        embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
        
        return embeddings
    
    def generate_document_embedding(
        self,
        document: Dict,
        fields: Optional[List[str]] = None
    ) -> np.ndarray:
        """Generate embedding for a document by combining multiple fields.
        
        Args:
            document: Document dictionary
            fields: List of fields to combine (default: ['title', 'abstract'])
            
        Returns:
            Numpy array of embedding (shape: [768])
        """
        if fields is None:
            fields = ['title', 'abstract']
        
        # Combine fields into single text
        text_parts = []
        for field in fields:
            if field in document and document[field]:
                text_parts.append(str(document[field]))
        
        combined_text = " ".join(text_parts)
        
        if not combined_text.strip():
            logger.warning("Empty document text, returning zero embedding")
            return np.zeros(768, dtype=np.float32)
        
        # Generate embedding
        embedding = self.encode_text(combined_text)[0]
        
        return embedding
    
    def generate_batch_embeddings(
        self,
        documents: List[Dict],
        fields: Optional[List[str]] = None,
        show_progress: bool = True
    ) -> List[np.ndarray]:
        """Generate embeddings for a batch of documents.
        
        Args:
            documents: List of document dictionaries
            fields: List of fields to combine
            show_progress: Show progress bar
            
        Returns:
            List of embeddings
        """
        if fields is None:
            fields = ['title', 'abstract']
        
        # Combine fields for all documents
        texts = []
        for doc in documents:
            text_parts = []
            for field in fields:
                if field in doc and doc[field]:
                    text_parts.append(str(doc[field]))
            
            combined_text = " ".join(text_parts)
            texts.append(combined_text if combined_text.strip() else " ")
        
        # Generate embeddings
        embeddings = self.encode_text(texts, show_progress=show_progress)
        
        return [emb for emb in embeddings]
    
    def compute_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Cosine similarity score (0-1)
        """
        # Normalize
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        
        return float(similarity)
    
    def find_similar(
        self,
        query_embedding: np.ndarray,
        document_embeddings: List[np.ndarray],
        top_k: int = 10
    ) -> List[tuple]:
        """Find most similar documents to query.
        
        Args:
            query_embedding: Query embedding
            document_embeddings: List of document embeddings
            top_k: Number of top results to return
            
        Returns:
            List of (index, similarity_score) tuples
        """
        similarities = []
        
        for idx, doc_emb in enumerate(document_embeddings):
            sim = self.compute_similarity(query_embedding, doc_emb)
            similarities.append((idx, sim))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
