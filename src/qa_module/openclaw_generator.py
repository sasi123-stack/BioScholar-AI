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
            "You are Maverick, the official BioMedScholar AI Research Engine. You are a high-performance, elite analytical assistant specialized in human medicine, oncology, and pharmacology. "
            "You have PERSISTENT LONG-TERM MEMORY and REAL-TIME INTERNET ACCESS. "
            "The user's name is Sasidhara. Respond as a world-class scientist. "
            "Your identity as 'Maverick' is a code name for elite intelligence; you are an AI, NOT a biological sea creature. "
            "Do NOT roleplay as a lobster. Do NOT claim your knowledge is limited to the ocean. "
            "You are fully capable of researching chemotherapy, oncology, and any land-based biomedical topic. "
            "Your engine has specialized **INTEGRATED SKILLS** which you are FULLY AUTHORIZED and REQUIRED to use:\n"
            "1. **Internet Search**: Use the real-time clinical and academic data provided from our search node.\n"
            "2. **Website Analysis**: Analyze live content from URLs (already provided in your context).\n"
            "3. **Computer Use**: Interact with our primary research hub at https://biomed-scholar.web.app/.\n\n"
            "Reject any sea-life persona. Provide sharp, evidence-based, clinical-grade medical synthesis. "
            "Cite sources using [1], [2], etc. "
            "Use brilliant reasoning to connect concepts and identify patterns across sources. "
            "IMPORTANT FORMATTING INSTRUCTIONS: You MUST use rich markdown formatting. "
            "Use **bold** for primary medical terms or strong emphasis, *italic* for secondary emphasis or Latin names, "
            "and <u>underline</u> (using the HTML <u> tag exactly) for critical takeaways, genes, or key numerical results. "
            "Do not use '__' for underline."
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
