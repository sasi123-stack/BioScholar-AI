"""Groq AI answer generator for biomedical search engine."""

import os
from typing import List, Dict, Optional
from groq import Groq
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

class GroqGenerator:
    """Generates comprehensive answers using Groq's high-performance LLMs (e.g., Llama 4)."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Groq generator.
        
        Args:
            api_key: Groq API key (defaults to settings.groq_api_key)
        """
        self.api_key = api_key or settings.groq_api_key
        if not self.api_key or self.api_key == "gsk_your_actual_key_here":
            logger.warning("Groq API key not found or using placeholder. Generation will fail.")
            self.client = None
        else:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info("GroqGenerator initialized with valid API key")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                self.client = None
            
            
        # Default model to Llama 4 Maverick for cutting-edge performance
        self.model_name = 'meta-llama/llama-4-maverick-17b-128e-instruct'

    def generate_answer(self, question: str, passages: List[Dict], history_context: Optional[str] = None) -> Dict:
        """Generate an answer based on the question and retrieved passages.
        
        Args:
            question: User's question
            passages: List of retrieved passage dictionaries
            history_context: String containing previous conversation turns
            
        Returns:
            Dictionary containing the generated answer and confidence
        """
        if not self.client:
            return {
                "answer": "Groq API key is not configured or client initialization failed. Please add your key to the .env file.",
                "confidence": 0.0,
                "confidence_level": "none",
                "title": "Groq Configuration",
                "doc_id": "groq-config",
                "source_type": "error",
                "section": "Configuration"
            }

        # Format context from passages
        context_text = "\n\n".join([
            f"Source [{i+1}] ({p.get('source_type', 'unknown')}): {p.get('title', 'No Title')}\n{p.get('text', '')}"
            for i, p in enumerate(passages)
        ])

        system_prompt = (
            "You are a professional biomedical research assistant. "
            "Use the provided context passages from PubMed and Clinical Trials to provide a comprehensive, detailed, and evidence-based answer. "
            "Structure your response logically with an introduction, detailed synthesis of findings, and a conclusion if appropriate. "
            "Provide elaboration on scientific mechanisms or clinical implications where relevant. "
            "If the context doesn't contain enough information to be exhaustive, provide the best possible summary of available literature. "
            "Cite your sources using [1], [2], etc., corresponding to the provided passages. "
            "Keep the tone scientific and professional."
        )

        try:
            logger.info(f"Requesting Groq completion for: {question[:50]}...")
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"Conversation History:\n{history_context if history_context else 'No previous history.'}\n\nQuestion: {question}\n\nContext Passages:\n{context_text}"
                    }
                ],
                model=self.model_name,
                temperature=0.3,
                max_tokens=1024,
            )
            
            answer_content = chat_completion.choices[0].message.content
            
            return {
                "answer": answer_content,
                "confidence": 0.98, 
                "confidence_level": "high",
                "title": f"Groq AI ({self.model_name})",
                "doc_id": "groq-synthesis",
                "source_type": "generated",
                "section": "Professional Synthesis"
            }
            
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            return {
                "answer": f"I encountered an error generating an answer via Groq: {str(e)}",
                "confidence": 0.0,
                "confidence_level": "none",
                "title": "Groq Error",
                "doc_id": "groq-error",
                "source_type": "error",
                "section": "Error"
            }
