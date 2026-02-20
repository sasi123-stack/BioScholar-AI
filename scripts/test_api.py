"""
Test script for REST API endpoints.
"""

import requests
import json
from typing import Dict, Any
from src.utils.logger import logger


BASE_URL = "http://localhost:8000/api/v1"


def print_json(data: Dict[str, Any]):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=2))


def test_health_check():
    """Test health check endpoint."""
    logger.info("=" * 60)
    logger.info("Testing Health Check")
    logger.info("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        logger.info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Health Status: {data['status']}")
            logger.info(f"   Elasticsearch: {'✅' if data['elasticsearch'] else '❌'}")
            logger.info(f"   Models Loaded: {'✅' if data['models_loaded'] else '❌'}")
            logger.info(f"   Version: {data['version']}")
        else:
            logger.error(f"❌ Health check failed: {response.text}")
    
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")


def test_statistics():
    """Test statistics endpoint."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Statistics")
    logger.info("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/statistics")
        logger.info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info("Index Statistics:")
            for index_name, stats in data.items():
                logger.info(f"  {index_name}:")
                logger.info(f"    Documents: {stats.get('document_count', 0)}")
                logger.info(f"    Exists: {stats.get('index_exists', False)}")
        else:
            logger.error(f"❌ Statistics failed: {response.text}")
    
    except Exception as e:
        logger.error(f"❌ Statistics error: {e}")


def test_search():
    """Test search endpoint."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Search")
    logger.info("=" * 60)
    
    queries = [
        {"query": "COVID-19 treatment", "index": "both", "max_results": 5},
        {"query": "diabetes management", "index": "pubmed", "max_results": 3},
        {"query": "cancer clinical trials", "index": "clinical_trials", "max_results": 3}
    ]
    
    for search_request in queries:
        logger.info(f"\n🔍 Query: '{search_request['query']}' (index: {search_request['index']})")
        
        try:
            response = requests.post(f"{BASE_URL}/search", json=search_request)
            logger.info(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Found {data['total_results']} results in {data['search_time_ms']:.2f}ms")
                
                for i, result in enumerate(data['results'][:3], 1):
                    logger.info(f"\n{i}. {result['title'][:80]}...")
                    logger.info(f"   Score: {result['score']:.4f}")
                    logger.info(f"   Source: {result['source']}")
                    logger.info(f"   ID: {result['id']}")
            else:
                logger.error(f"❌ Search failed: {response.text}")
        
        except Exception as e:
            logger.error(f"❌ Search error: {e}")


def test_question_answering():
    """Test question answering endpoint."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Question Answering")
    logger.info("=" * 60)
    
    questions = [
        {"question": "What is the treatment for COVID-19?", "max_answers": 3},
        {"question": "How is diabetes managed?", "max_answers": 2},
        {"question": "What are the symptoms of hypertension?", "max_answers": 2}
    ]
    
    for qa_request in questions:
        logger.info(f"\n❓ Question: '{qa_request['question']}'")
        
        try:
            response = requests.post(f"{BASE_URL}/question", json=qa_request)
            logger.info(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Status: {data['status']} (time: {data['qa_time_ms']:.2f}ms)")
                logger.info(f"   Found {len(data['answers'])} answers from {len(data['passages'])} passages")
                
                for i, answer in enumerate(data['answers'], 1):
                    logger.info(f"\n   Answer {i}: {answer['answer']}")
                    logger.info(f"   Confidence: {answer['confidence']:.4f} ({answer['confidence_level']})")
                    logger.info(f"   Source: {answer['source_title'][:60]}...")
                    logger.info(f"   Section: {answer['section']}")
            else:
                logger.error(f"❌ QA failed: {response.text}")
        
        except Exception as e:
            logger.error(f"❌ QA error: {e}")


def test_batch_question_answering():
    """Test batch question answering endpoint."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Batch Question Answering")
    logger.info("=" * 60)
    
    batch_request = {
        "questions": [
            "What causes COVID-19?",
            "How is cancer treated?",
            "What is the role of insulin?"
        ],
        "max_answers_per_question": 1
    }
    
    logger.info(f"Processing {len(batch_request['questions'])} questions...")
    
    try:
        response = requests.post(f"{BASE_URL}/batch-question", json=batch_request)
        logger.info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Batch completed in {data['total_time_ms']:.2f}ms")
            
            for i, result in enumerate(data['results'], 1):
                logger.info(f"\n{i}. Q: {result['question']}")
                if result['answers']:
                    answer = result['answers'][0]
                    logger.info(f"   A: {answer['answer']}")
                    logger.info(f"   Confidence: {answer['confidence']:.4f}")
                else:
                    logger.info(f"   A: No answer found")
        else:
            logger.error(f"❌ Batch QA failed: {response.text}")
    
    except Exception as e:
        logger.error(f"❌ Batch QA error: {e}")


def test_get_document():
    """Test document retrieval endpoint."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Document Retrieval")
    logger.info("=" * 60)
    
    # First, get a document ID from search
    try:
        search_response = requests.post(
            f"{BASE_URL}/search",
            json={"query": "diabetes", "max_results": 1}
        )
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data['results']:
                result = search_data['results'][0]
                doc_id = result['id']
                index = f"{result['source']}_articles" if result['source'] == "pubmed" else "clinical_trials"
                
                logger.info(f"📄 Retrieving document: {doc_id} from {index}")
                
                doc_response = requests.get(
                    f"{BASE_URL}/document/{doc_id}",
                    params={"index": index, "include_embedding": False}
                )
                
                logger.info(f"Status Code: {doc_response.status_code}")
                
                if doc_response.status_code == 200:
                    doc_data = doc_response.json()
                    logger.info(f"✅ Document retrieved successfully")
                    logger.info(f"   Title: {doc_data['title'][:80]}...")
                    logger.info(f"   Source: {doc_data['source']}")
                    logger.info(f"   Has abstract: {doc_data['abstract'] is not None}")
                    logger.info(f"   Has full text: {doc_data['full_text'] is not None}")
                else:
                    logger.error(f"❌ Document retrieval failed: {doc_response.text}")
            else:
                logger.info("No documents found in search")
        else:
            logger.error(f"❌ Search failed: {search_response.text}")
    
    except Exception as e:
        logger.error(f"❌ Document retrieval error: {e}")


def main():
    """Run all API tests."""
    logger.info("\n" + "🧪 Starting API Tests" + "\n")
    logger.info("Make sure the API server is running: python -m uvicorn src.api.app:app --reload\n")
    
    try:
        # Test all endpoints
        test_health_check()
        test_statistics()
        test_search()
        test_question_answering()
        test_batch_question_answering()
        test_get_document()
        
        logger.info("\n" + "=" * 60)
        logger.info("✨ All API tests completed!")
        logger.info("=" * 60)
    
    except KeyboardInterrupt:
        logger.info("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        logger.error(f"\n\n❌ Test suite failed: {e}")


if __name__ == "__main__":
    main()
