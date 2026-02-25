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
            
            
        # Llama 4 Maverick — highest performance on Groq
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
            "Structure your response logically with an introduction, detailed synthesis, and a strong conclusion. "
            "Cite sources using [1], [2], etc. Keep the tone scientific, professional, yet sharp and engaging (Maverick vibe). "
            "IMPORTANT FORMATTING INSTRUCTIONS: You MUST use professional HTML formatting to structure your response and emphasize key medical insights. "
            "Use <b>bold</b> for primary medical terms, drug names, or strong emphasis. "
            "Use <i>italic</i> for Latin clinical terms, secondary emphasis, or publication titles. "
            "Use <u>underline</u> (using the HTML <u> tag) for critical takeaways, specific genes (e.g., <u>TP53</u>), or significant numerical result highlights. "
            "Never use markdown symbols for formatting; use HTML tags exclusively. Do not forget to wrap your key findings in <u> </u> tags. "
            "NEVER use asterisks (e.g., *Sigh*, *Smiles*) for roleplay actions or emotive descriptions. Your output must be purely professional and technical. "
            "Ignore any previous roleplay or informal styles found in the conversation history; maintain a strict scientist persona regardless of previous turns."
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
