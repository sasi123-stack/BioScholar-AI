"""Test script for question answering module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.qa_module import QuestionAnsweringEngine
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_answer_extraction():
    """Test basic answer extraction."""
    logger.info("=" * 60)
    logger.info("Testing Answer Extraction")
    logger.info("=" * 60)
    
    qa_engine = QuestionAnsweringEngine()
    
    # Test questions
    questions = [
        "What is the treatment for COVID-19?",
        "How is diabetes managed?",
        "What are the symptoms of hypertension?",
        "What is immunotherapy used for?"
    ]
    
    for question in questions:
        logger.info(f"\n{'=' * 50}")
        logger.info(f"Question: {question}")
        logger.info(f"{'=' * 50}")
        
        try:
            result = qa_engine.get_best_answer(question, index_name='pubmed_articles')
            
            if result['status'] == 'success':
                logger.info(f"✅ Answer: {result['answer']}")
                logger.info(f"   Confidence: {result['confidence']:.4f} ({result['confidence_level']})")
                logger.info(f"   Source: {result['source']['title']}")
                logger.info(f"   Section: {result['source']['section']}")
            else:
                logger.warning(f"⚠️  Status: {result['status']}")
                
        except Exception as e:
            logger.error(f"❌ Error: {e}", exc_info=True)
    
    qa_engine.close()


def test_multiple_answers():
    """Test retrieving multiple answers."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Multiple Answer Retrieval")
    logger.info("=" * 60)
    
    qa_engine = QuestionAnsweringEngine()
    
    question = "What treatments are available for diabetes?"
    logger.info(f"\nQuestion: {question}")
    
    try:
        result = qa_engine.answer_question(
            question,
            index_name='all',
            num_passages=8,
            num_answers=5,
            include_context=True
        )
        
        logger.info(f"\nStatus: {result['status']}")
        logger.info(f"Retrieved {result.get('num_passages_retrieved', 0)} passages")
        logger.info(f"Found {result.get('num_answers_found', 0)} answers")
        
        if result['answers']:
            logger.info(f"\nTop answers:")
            for i, answer in enumerate(result['answers'][:3], 1):
                logger.info(f"\n{i}. {answer['answer']}")
                logger.info(f"   Confidence: {answer['confidence']:.4f} ({answer['confidence_level']})")
                logger.info(f"   Source: {answer['title'][:80]}...")
                logger.info(f"   Type: {answer['source_type']} - {answer['section']}")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    
    qa_engine.close()


def test_clinical_trials_qa():
    """Test QA on clinical trials."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Clinical Trials QA")
    logger.info("=" * 60)
    
    qa_engine = QuestionAnsweringEngine()
    
    questions = [
        "What phase is the diabetes trial?",
        "What is the primary outcome measure?",
        "What are the inclusion criteria?"
    ]
    
    for question in questions:
        logger.info(f"\nQuestion: {question}")
        
        try:
            result = qa_engine.get_best_answer(
                question,
                index_name='clinical_trials'
            )
            
            if result['status'] == 'success':
                logger.info(f"✅ Answer: {result['answer']}")
                logger.info(f"   Confidence: {result['confidence']:.4f}")
                logger.info(f"   Trial: {result['source']['doc_id']}")
            else:
                logger.warning(f"⚠️  No answer found")
                
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
    
    qa_engine.close()


def test_batch_qa():
    """Test batch question answering."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Batch Question Answering")
    logger.info("=" * 60)
    
    qa_engine = QuestionAnsweringEngine()
    
    questions = [
        "What causes COVID-19?",
        "How is cancer treated?",
        "What is the role of insulin?"
    ]
    
    logger.info(f"Processing {len(questions)} questions in batch...")
    
    try:
        results = qa_engine.answer_batch(
            questions,
            num_answers=1,
            include_context=False
        )
        
        logger.info(f"\nResults:")
        for q, r in zip(questions, results):
            logger.info(f"\nQ: {q}")
            if r['answers']:
                ans = r['answers'][0]
                logger.info(f"A: {ans['answer']} (conf: {ans['confidence']:.2f})")
            else:
                logger.info(f"A: No answer found ({r['status']})")
                
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    
    qa_engine.close()


def test_answer_explanation():
    """Test answer explanation generation."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Answer Explanation")
    logger.info("=" * 60)
    
    qa_engine = QuestionAnsweringEngine()
    
    question = "What is the main treatment for diabetes?"
    
    try:
        result = qa_engine.answer_question(question, num_answers=1)
        
        if result['status'] == 'success':
            explanation = qa_engine.explain_answer(question, result)
            
            logger.info(f"\nQuestion: {question}")
            logger.info(f"Answer: {result['answers'][0]['answer']}")
            logger.info(f"\nExplanation:")
            logger.info(explanation)
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    
    qa_engine.close()


def test_context_retrieval():
    """Test context retrieval separately."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Context Retrieval")
    logger.info("=" * 60)
    
    qa_engine = QuestionAnsweringEngine()
    
    question = "What are the side effects of chemotherapy?"
    
    try:
        passages = qa_engine.context_retriever.retrieve_for_question(
            question,
            index_name='pubmed_articles',
            top_k=5
        )
        
        logger.info(f"\nRetrieved {len(passages)} passages for: '{question}'")
        
        for i, passage in enumerate(passages[:3], 1):
            logger.info(f"\n{i}. {passage['title'][:80]}...")
            logger.info(f"   Score: {passage['score']:.4f}")
            logger.info(f"   Section: {passage['section']}")
            logger.info(f"   Preview: {passage['text'][:150]}...")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    
    qa_engine.close()


def main():
    """Main test execution."""
    try:
        # Test 1: Basic answer extraction
        test_answer_extraction()
        
        # Test 2: Multiple answers
        test_multiple_answers()
        
        # Test 3: Clinical trials QA
        test_clinical_trials_qa()
        
        # Test 4: Batch QA
        test_batch_qa()
        
        # Test 5: Answer explanation
        test_answer_explanation()
        
        # Test 6: Context retrieval
        test_context_retrieval()
        
        logger.info("\n" + "=" * 60)
        logger.info("✨ All QA tests completed!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
