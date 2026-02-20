"""Model loader for BioBERT and ClinicalBERT models."""

import torch
from pathlib import Path
from typing import Optional, Tuple
from transformers import (
    AutoTokenizer, 
    AutoModel,
    AutoModelForQuestionAnswering
)

from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ModelLoader:
    """Load and manage transformer models for biomedical NLP."""
    
    def __init__(
        self,
        cache_dir: Optional[str] = None,
        device: Optional[str] = None
    ):
        """Initialize model loader.
        
        Args:
            cache_dir: Directory to cache downloaded models
            device: Device to load models on ('cuda', 'cpu', or None for auto)
        """
        self.cache_dir = cache_dir or settings.model_cache_dir
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        
        # Auto-detect device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        logger.info(f"Model loader initialized with device: {self.device}")
        
        self._models = {}
        self._tokenizers = {}
    
    def load_biobert(self) -> Tuple[AutoModel, AutoTokenizer]:
        """Load BioBERT model and tokenizer.
        
        Returns:
            Tuple of (model, tokenizer)
        """
        model_name = settings.biobert_model
        
        if model_name in self._models:
            logger.info(f"Using cached BioBERT model: {model_name}")
            return self._models[model_name], self._tokenizers[model_name]
        
        logger.info(f"Loading BioBERT model: {model_name}")
        
        try:
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=self.cache_dir
            )
            
            model = AutoModel.from_pretrained(
                model_name,
                cache_dir=self.cache_dir
            )
            
            model = model.to(self.device)
            model.eval()
            
            self._models[model_name] = model
            self._tokenizers[model_name] = tokenizer
            
            logger.info(f"✅ BioBERT loaded successfully on {self.device}")
            
            return model, tokenizer
            
        except Exception as e:
            logger.error(f"Failed to load BioBERT: {e}", exc_info=True)
            raise
    
    def load_clinicalbert(self) -> Tuple[AutoModel, AutoTokenizer]:
        """Load ClinicalBERT model and tokenizer.
        
        Returns:
            Tuple of (model, tokenizer)
        """
        model_name = settings.clinicalbert_model
        
        if model_name in self._models:
            logger.info(f"Using cached ClinicalBERT model: {model_name}")
            return self._models[model_name], self._tokenizers[model_name]
        
        logger.info(f"Loading ClinicalBERT model: {model_name}")
        
        try:
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=self.cache_dir
            )
            
            model = AutoModel.from_pretrained(
                model_name,
                cache_dir=self.cache_dir
            )
            
            model = model.to(self.device)
            model.eval()
            
            self._models[model_name] = model
            self._tokenizers[model_name] = tokenizer
            
            logger.info(f"✅ ClinicalBERT loaded successfully on {self.device}")
            
            return model, tokenizer
            
        except Exception as e:
            logger.error(f"Failed to load ClinicalBERT: {e}", exc_info=True)
            raise
    
    def load_qa_model(self) -> Tuple[AutoModelForQuestionAnswering, AutoTokenizer]:
        """Load Question Answering model (BioBERT fine-tuned on SQuAD).
        
        Returns:
            Tuple of (model, tokenizer)
        """
        model_name = settings.biobert_qa_model
        
        if model_name in self._models:
            logger.info(f"Using cached QA model: {model_name}")
            return self._models[model_name], self._tokenizers[model_name]
        
        logger.info(f"Loading QA model: {model_name}")
        
        try:
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=self.cache_dir
            )
            
            model = AutoModelForQuestionAnswering.from_pretrained(
                model_name,
                cache_dir=self.cache_dir
            )
            
            model = model.to(self.device)
            model.eval()
            
            self._models[model_name] = model
            self._tokenizers[model_name] = tokenizer
            
            logger.info(f"✅ QA model loaded successfully on {self.device}")
            
            return model, tokenizer
            
        except Exception as e:
            logger.error(f"Failed to load QA model: {e}", exc_info=True)
            raise
    
    def get_device(self) -> str:
        """Get current device.
        
        Returns:
            Device string ('cuda' or 'cpu')
        """
        return self.device
    
    def clear_cache(self):
        """Clear cached models from memory."""
        self._models.clear()
        self._tokenizers.clear()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info("Model cache cleared")
