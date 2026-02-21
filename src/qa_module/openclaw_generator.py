"""OpenClaw (or generic OpenAI-compatible) answer generator."""

import os
from typing import List, Dict, Optional
from openai import OpenAI
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

class OpenClawGenerator:
    """Generates answers using an OpenClaw agent or an OpenAI-compatible endpoint."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize generator.
        
        Args:
            api_key: API key for the service (defaults to settings.openclaw_api_key)
            base_url: Base URL for the service (defaults to settings.openclaw_api_base)
        """
        self.api_key = api_key or settings.openclaw_api_key
        self.base_url = base_url or settings.openclaw_api_base
        
        if not self.api_key or self.api_key == "sk-openclaw-placeholder":
            logger.warning("OpenClaw API key not configured or using placeholder.")
            
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            logger.info(f"OpenClawGenerator initialized (Base: {self.base_url})")
        except Exception as e:
            logger.error(f"Failed to initialize OpenClaw client: {e}")
            self.client = None

    def generate_answer(self, question: str, passages: List[Dict], history_context: Optional[str] = None) -> Dict:
        """Generate answer using OpenClaw/OpenAI."""
        if not self.client:
             return {
                "answer": "OpenClaw client failed to initialize.",
                "confidence": 0.0,
                "confidence_level": "none",
                "status": "error"
            }

        # Format context
        context_text = "\n\n".join([
            f"Source [{i+1}] ({p.get('source_type', 'unknown')}): {p.get('title', 'No Title')}\n{p.get('text', '')}"
            for i, p in enumerate(passages)
        ])

        system_prompt = (
            "You are a biomedical research assistant powered by Llama 3.3 70B, a powerful open-source AI model. "
            "Using the provided context passages, synthesize a comprehensive, evidence-based answer to the user's question. "
            "Cite sources using [1], [2], etc. "
            "If the answer is not in the context, state that clearly but provide relevant scientific background if appropriate. "
            "Use clear reasoning to connect concepts and identify patterns across sources."
        )

        user_content = f"Conversation History:\n{history_context if history_context else 'No previous history.'}\n\nQuestion: {question}\n\nContext:\n{context_text}"

        try:
            logger.info(f"Requesting OpenClaw completion for: {question[:50]}...")
            
            # Using OpenRouter's FREE Llama 3.3 70B - no credit card required!
            # OpenRouter provides free access to Llama models
            response = self.client.chat.completions.create(
                model="meta-llama/llama-3.3-70b-instruct", # OpenRouter's free Llama 3.3 70B
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            answer_content = response.choices[0].message.content
            
            return {
                "answer": answer_content,
                "confidence": 0.90,
                "confidence_level": "high",
                "title": "OpenClaw AI Synthesis",
                "doc_id": "openclaw-synthesis",
                "source_type": "generated",
                "section": "Synthesis"
            }
            
        except Exception as e:
            logger.error(f"OpenClaw generation failed: {e}")
            return {
                "answer": f"OpenClaw error: {str(e)}",
                "confidence": 0.0,
                "confidence_level": "none",
                "title": "Error",
                "doc_id": "error",
                "source_type": "error",
                "section": "Error"
            }
