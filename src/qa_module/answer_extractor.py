"""Answer extractor using transformer-based QA models."""

import torch
from typing import List, Dict, Optional, Tuple
from transformers import AutoTokenizer, AutoModelForQuestionAnswering

from src.utils.logger import get_logger
from src.nlp_engine import ModelLoader

logger = get_logger(__name__)


class AnswerExtractor:
    """Extract answers from context using QA models."""
    
    def __init__(
        self,
        model_loader: Optional[ModelLoader] = None,
        confidence_threshold: float = 0.01,
        max_answer_length: int = 200
    ):
        """Initialize answer extractor.
        
        Args:
            model_loader: Model loader instance
            confidence_threshold: Minimum confidence score for answers
            max_answer_length: Maximum length of extracted answer
        """
        self.model_loader = model_loader or ModelLoader()
        self.confidence_threshold = confidence_threshold
        self.max_answer_length = max_answer_length
        
        # Load QA model
        logger.info("Loading QA model...")
        self.model, self.tokenizer = self.model_loader.load_qa_model()
        self.device = self.model_loader.get_device()
        
        logger.info(f"AnswerExtractor initialized on {self.device}")
    
    def extract_answer(
        self,
        question: str,
        context: str
    ) -> Dict:
        """Extract answer from a single context passage.
        
        Args:
            question: User question
            context: Context passage
            
        Returns:
            Dictionary with answer, score, and positions
        """
        # Tokenize
        inputs = self.tokenizer(
            question,
            context,
            add_special_tokens=True,
            return_tensors="pt",
            max_length=512,
            truncation=True,
            padding=True
        )
        
        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Get predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Get answer span
        start_logits = outputs.start_logits[0]
        end_logits = outputs.end_logits[0]
        
        # Get best start and end positions
        start_idx = torch.argmax(start_logits).item()
        end_idx = torch.argmax(end_logits).item()
        
        # Get confidence scores
        start_score = torch.softmax(start_logits, dim=0)[start_idx].item()
        end_score = torch.softmax(end_logits, dim=0)[end_idx].item()
        confidence = (start_score + end_score) / 2
        
        # Extract answer text
        if start_idx <= end_idx and end_idx < len(inputs['input_ids'][0]):
            answer_tokens = inputs['input_ids'][0][start_idx:end_idx + 1]
            answer_text = self.tokenizer.decode(answer_tokens, skip_special_tokens=True)
        else:
            answer_text = ""
            confidence = 0.0
        
        return {
            'answer': answer_text,
            'confidence': confidence,
            'start_idx': start_idx,
            'end_idx': end_idx
        }
    
    def extract_from_passages(
        self,
        question: str,
        passages: List[Dict],
        top_k: int = 3
    ) -> List[Dict]:
        """Extract answers from multiple passages.
        
        Args:
            question: User question
            passages: List of passage dictionaries
            top_k: Number of top answers to return
            
        Returns:
            List of answer dictionaries with metadata
        """
        logger.info(f"Extracting answers from {len(passages)} passages")
        
        answers = []
        
        for passage in passages:
            context = passage.get('text', '')
            if not context:
                continue
            
            # Extract answer
            result = self.extract_answer(question, context)
            
            # Only include if above threshold
            if result['confidence'] >= self.confidence_threshold and result['answer']:
                answers.append({
                    'answer': result['answer'],
                    'confidence': result['confidence'],
                    'passage': passage,
                    'title': passage.get('title', ''),
                    'doc_id': passage.get('doc_id', ''),
                    'section': passage.get('section', ''),
                    'source_type': passage.get('source_type', ''),
                    'journal': passage.get('journal', ''),
                    'publication_date': passage.get('publication_date', '')
                })
        
        # Sort by confidence
        answers.sort(key=lambda x: x['confidence'], reverse=True)
        
        logger.info(f"Found {len(answers)} valid answers (threshold={self.confidence_threshold})")
        
        return answers[:top_k]
    
    def extract_with_context_window(
        self,
        question: str,
        context: str,
        window_size: int = 100
    ) -> Dict:
        """Extract answer with surrounding context.
        
        Args:
            question: User question
            context: Full context
            window_size: Characters before/after answer to include
            
        Returns:
            Dictionary with answer and surrounding context
        """
        result = self.extract_answer(question, context)
        
        if not result['answer']:
            return result
        
        # Find answer position in original context
        answer = result['answer']
        answer_pos = context.find(answer)
        
        if answer_pos == -1:
            return result
        
        # Extract context window
        start = max(0, answer_pos - window_size)
        end = min(len(context), answer_pos + len(answer) + window_size)
        
        context_window = context[start:end]
        
        # Add to result
        result['context_window'] = context_window
        result['answer_position'] = answer_pos
        
        return result
    
    def batch_extract(
        self,
        questions: List[str],
        contexts: List[str]
    ) -> List[Dict]:
        """Extract answers for multiple question-context pairs.
        
        Args:
            questions: List of questions
            contexts: List of contexts
            
        Returns:
            List of answer dictionaries
        """
        if len(questions) != len(contexts):
            raise ValueError("Number of questions must match number of contexts")
        
        results = []
        
        for question, context in zip(questions, contexts):
            result = self.extract_answer(question, context)
            results.append(result)
        
        return results
    
    def get_answer_confidence_level(self, confidence: float) -> str:
        """Categorize confidence level.
        
        Args:
            confidence: Confidence score
            
        Returns:
            Confidence level string
        """
        if confidence >= 0.8:
            return "high"
        elif confidence >= 0.5:
            return "medium"
        elif confidence >= 0.2:
            return "low"
        else:
            return "very_low"
