"""DeepSeek AI answer generator for biomedical search engine."""

import os
from typing import List, Dict, Optional
from openai import OpenAI
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

class DeepSeekGenerator:
    """Generates comprehensive answers using DeepSeek LLM based on retrieved context."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize DeepSeek generator.
        
        Args:
            api_key: DeepSeek API key (defaults to settings.deepseek_api_key)
        """
        self.api_key = api_key or settings.deepseek_api_key
        if not self.api_key or self.api_key == "your_deepseek_api_key_here":
            logger.warning("DeepSeek API key not found or using placeholder. Generation will fail.")
            
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        logger.info("DeepSeekGenerator initialized")

    def generate_answer(self, question: str, passages: List[Dict]) -> Dict:
        """Generate an answer based on the question and retrieved passages.
        
        Args:
            question: User's question
            passages: List of retrieved passage dictionaries
            
        Returns:
            Dictionary containing the generated answer and confidence
        """
        if not self.api_key or self.api_key == "your_deepseek_api_key_here":
            return {
                "answer": "DeepSeek API key is not configured. Please add your key to the .env file.",
                "confidence": 0.0,
                "confidence_level": "none"
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
            "Cite your sources using [1], [2], etc., corresponding to the provided passages."
        )

        user_content = f"Question: {question}\n\nContext Passages:\n{context_text}"

        try:
            logger.info(f"Requesting DeepSeek completion for: {question[:50]}...")
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.3, # Low temperature for factual accuracy
                max_tokens=1000
            )
            
            answer_content = response.choices[0].message.content
            
            return {
                "answer": answer_content,
                "confidence": 0.95, # LLM generated, assigning high relative confidence
                "confidence_level": "high",
                "title": "DeepSeek AI (Synthetic Synthesis)",
                "doc_id": "deepseek-synthesis",
                "source_type": "generated",
                "section": "Multi-source Synthesis"
            }
            
        except Exception as e:
            logger.error(f"DeepSeek generation failed: {e}")
            return {
                "answer": f"I encountered an error generating an answer via DeepSeek: {str(e)}",
                "confidence": 0.0,
                "confidence_level": "none",
                "title": "DeepSeek Error",
                "doc_id": "deepseek-error",
                "source_type": "error",
                "section": "Error"
            }
