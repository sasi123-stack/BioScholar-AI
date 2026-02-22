"""Question answering engine combining retrieval and extraction."""

from typing import List, Dict, Optional
from src.utils.logger import get_logger
from .context_retriever import ContextRetriever
from .answer_extractor import AnswerExtractor
from .gemini_generator import GeminiGenerator
from .groq_generator import GroqGenerator
from .openclaw_generator import OpenClawGenerator

logger = get_logger(__name__)


class QuestionAnsweringEngine:
    """End-to-end question answering system."""
    
    def __init__(
        self,
        context_retriever: Optional[ContextRetriever] = None,
        answer_extractor: Optional[AnswerExtractor] = None,
        answer_generator: Optional[GeminiGenerator] = None,
        groq_generator: Optional[GroqGenerator] = None,
        openclaw_generator: Optional[OpenClawGenerator] = None
    ):
        """Initialize QA engine."""
        self.context_retriever = context_retriever or ContextRetriever()
        self.answer_extractor = answer_extractor or AnswerExtractor()
        self.answer_generator = answer_generator or GeminiGenerator()
        self.groq_generator = groq_generator or GroqGenerator()
        self.openclaw_generator = openclaw_generator or OpenClawGenerator()
        
        logger.info("QuestionAnsweringEngine initialized (OpenClaw, Gemini & Groq ready)")
    
    def answer_question(
        self,
        question: str,
        index_name: str = 'pubmed_articles',
        num_passages: int = 5,
        num_answers: int = 3,
        include_context: bool = True,
        history_context: Optional[str] = None
    ) -> Dict:
        """Answer a question using retrieval and extraction."""
        logger.info(f"Answering question: '{question}'")
        
        # Step 1: Retrieve relevant passages
        passages = self.context_retriever.retrieve_for_question(
            question,
            index_name=index_name,
            top_k=num_passages
        )
        
        if not passages:
            logger.warning("No passages retrieved")
            return {
                'question': question,
                'answers': [],
                'passages': [],
                'status': 'no_results'
            }
        
        # Step 2: Generate/Extract answers from passages
        generated_answer = None
        
        # Prefer OpenClaw if configured (User requested priority)
        if self.openclaw_generator and self.openclaw_generator.api_key != "sk-openclaw-placeholder":
             logger.info("Using OpenClaw for synthesis")
             generated_answer = self.openclaw_generator.generate_answer(question, passages, history_context=history_context)
        
        # Fallback to Groq
        elif self.groq_generator.api_key and self.groq_generator.api_key != "gsk_your_actual_key_here":
            logger.info("Using Groq for lightning-fast conversational synthesis")
            generated_answer = self.groq_generator.generate_answer(question, passages, history_context=history_context)
        # Fallback to Gemini
        elif self.answer_generator.api_key and self.answer_generator.api_key != "your_gemini_api_key_here":
            logger.info("Using Gemini for conversational synthesis")
            generated_answer = self.answer_generator.generate_answer(question, passages, history_context=history_context)
        
        # Always run extraction for validation/secondary options
        extracted_answers = self.answer_extractor.extract_from_passages(
            question,
            passages,
            top_k=num_answers
        )
        
        # Construct final answers list
        final_answers = []
        if generated_answer:
            final_answers.append(generated_answer)
        
        # Add extracted answers, avoiding duplicates if possible (or just append)
        formatted_extracted = self._format_answers(extracted_answers)
        final_answers.extend(formatted_extracted)
        
        if not final_answers:
            logger.warning("No valid answers found")
            return {
                'question': question,
                'answers': [],
                'passages': passages if include_context else [],
                'status': 'no_answers'
            }
        
        # Step 3: Format response
        response = {
            'question': question,
            'answers': final_answers[:num_answers + 1], # Allow one extra for the synthesis
            'passages': passages if include_context else [],
            'status': 'success',
            'num_passages_retrieved': len(passages),
            'num_answers_found': len(final_answers)
        }
        
        logger.info(f"✅ Found {len(final_answers)} answers from {len(passages)} passages")
        
        return response
    
    def answer_batch(
        self,
        questions: List[str],
        **kwargs
    ) -> List[Dict]:
        """Answer multiple questions.
        
        Args:
            questions: List of questions
            **kwargs: Additional arguments for answer_question
            
        Returns:
            List of answer dictionaries
        """
        logger.info(f"Answering {len(questions)} questions")
        
        results = []
        for question in questions:
            result = self.answer_question(question, **kwargs)
            results.append(result)
        
        return results
    
    def answer_with_followup(
        self,
        question: str,
        previous_context: Optional[List[Dict]] = None,
        **kwargs
    ) -> Dict:
        """Answer question considering previous context (for follow-up questions).
        
        Args:
            question: User question
            previous_context: Context from previous question
            **kwargs: Additional arguments
            
        Returns:
            Answer dictionary
        """
        # For now, just answer normally
        # In production, implement context-aware QA
        return self.answer_question(question, **kwargs)
    
    def get_best_answer(
        self,
        question: str,
        **kwargs
    ) -> Dict:
        """Get single best answer for a question.
        
        Args:
            question: User question
            **kwargs: Additional arguments
            
        Returns:
            Best answer dictionary
        """
        result = self.answer_question(question, num_answers=1, **kwargs)
        
        if result['status'] == 'success' and result['answers']:
            best = result['answers'][0]
            return {
                'question': question,
                'answer': best['answer'],
                'confidence': best['confidence'],
                'confidence_level': best['confidence_level'],
                'source': {
                    'title': best['title'],
                    'doc_id': best['doc_id'],
                    'section': best['section']
                },
                'status': 'success'
            }
        else:
            return {
                'question': question,
                'answer': None,
                'confidence': 0.0,
                'status': result['status']
            }
    
    def _format_answers(self, answers: List[Dict]) -> List[Dict]:
        """Format answers for response.
        
        Args:
            answers: Raw answer dictionaries
            
        Returns:
            Formatted answer dictionaries
        """
        formatted = []
        
        for answer in answers:
            formatted.append({
                'answer': answer['answer'],
                'confidence': round(answer['confidence'], 4),
                'confidence_level': self.answer_extractor.get_answer_confidence_level(
                    answer['confidence']
                ),
                'title': answer['title'],
                'doc_id': answer['doc_id'],
                'section': answer['section'],
                'source_type': answer['source_type'],
                'journal': answer.get('journal', ''),
                'publication_date': answer.get('publication_date', '')
            })
        
        return formatted
    
    def explain_answer(
        self,
        question: str,
        answer_result: Dict
    ) -> str:
        """Generate explanation for an answer.
        
        Args:
            question: Original question
            answer_result: Answer result dictionary
            
        Returns:
            Explanation string
        """
        if answer_result['status'] != 'success' or not answer_result['answers']:
            return "No answer could be found for this question."
        
        best = answer_result['answers'][0]
        
        explanation = f"Based on the question '{question}', "
        explanation += f"the answer '{best['answer']}' was found "
        explanation += f"in {best['title']} ({best['section']}) "
        explanation += f"with {best['confidence_level']} confidence "
        explanation += f"(score: {best['confidence']:.2f})."
        
        return explanation
    
    def get_supporting_evidence(
        self,
        question: str,
        answer: str,
        passages: List[Dict]
    ) -> List[str]:
        """Get supporting evidence for an answer.
        
        Args:
            question: Original question
            answer: Extracted answer
            passages: Retrieved passages
            
        Returns:
            List of evidence snippets
        """
        evidence = []
        
        for passage in passages:
            text = passage.get('text', '')
            if answer.lower() in text.lower():
                # Find context around answer
                idx = text.lower().find(answer.lower())
                start = max(0, idx - 100)
                end = min(len(text), idx + len(answer) + 100)
                snippet = text[start:end]
                evidence.append(snippet)
        
        return evidence
    
    def close(self):
        """Close connections."""
        if self.context_retriever:
            self.context_retriever.close()
