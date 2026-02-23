"""Gemini AI answer generator for biomedical search engine."""

import os
from typing import List, Dict, Optional
import google.generativeai as genai
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

class GeminiGenerator:
    """Generates comprehensive answers using Google Gemini LLM based on retrieved context."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini generator.
        
        Args:
            api_key: Gemini API key (defaults to settings.gemini_api_key)
        """
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            logger.warning("Gemini API key not found or using placeholder. Generation will fail.")
        else:
            genai.configure(api_key=self.api_key)
            logger.info("GeminiGenerator initialized with valid API key")
            
        # Default model to 1.5 Flash (or 2.0 Flash if available)
        self.model_name = 'gemini-1.5-flash'
        try:
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")

    def generate_answer(self, question: str, passages: List[Dict], history_context: Optional[str] = None) -> Dict:
        """Generate an answer based on the question and retrieved passages.
        
        Args:
            question: User's question
            passages: List of retrieved passage dictionaries
            history_context: String containing previous conversation turns
            
        Returns:
            Dictionary containing the generated answer and confidence
        """
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return {
                "answer": "Gemini API key is not configured. Please add your key to the .env file.",
                "confidence": 0.0,
                "confidence_level": "none",
                "title": "Gemini Configuration",
                "doc_id": "gemini-config",
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
            "Cite your sources using [1], [2], etc. "
            "IMPORTANT FORMATTING INSTRUCTIONS: You MUST use rich markdown formatting. "
            "Use **bold** for primary medical terms or strong emphasis, *italic* for secondary emphasis or Latin names, "
            "and <u>underline</u> (using the HTML <u> tag exactly) for critical takeaways, genes, or key numerical results. "
            "Never use '__' for underline."
        )

        prompt = f"{system_prompt}\n\nConversation History:\n{history_context if history_context else 'No previous history.'}\n\nQuestion: {question}\n\nContext Passages:\n{context_text}"

        try:
            logger.info(f"Requesting Gemini completion for: {question[:50]}...")
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1000,
                )
            )
            
            answer_content = response.text
            
            return {
                "answer": answer_content,
                "confidence": 0.95, 
                "confidence_level": "high",
                "title": "Gemini AI (Synthetic Synthesis)",
                "doc_id": "gemini-synthesis",
                "source_type": "generated",
                "section": "Multi-source Synthesis"
            }
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return {
                "answer": f"I encountered an error generating an answer via Gemini: {str(e)}",
                "confidence": 0.0,
                "confidence_level": "none",
                "title": "Gemini Error",
                "doc_id": "gemini-error",
                "source_type": "error",
                "section": "Error"
            }
