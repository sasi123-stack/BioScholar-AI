"""Integration tests for the complete system."""

import pytest
import requests
import time
from typing import Dict, List

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
FRONTEND_URL = "http://localhost:8080"


class TestSystemHealth:
    """Test system health and availability."""
    
    def test_api_health_check(self):
        """Test API health endpoint."""
        response = requests.get(f"{API_BASE_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "elasticsearch" in data
        assert data["elasticsearch"] is True
    
    def test_api_statistics(self):
        """Test statistics endpoint."""
        response = requests.get(f"{API_BASE_URL}/statistics")
        assert response.status_code == 200
        
        data = response.json()
        assert "pubmed_articles" in data
        assert "clinical_trials" in data
        assert data["pubmed_articles"]["document_count"] > 0
        assert data["clinical_trials"]["document_count"] > 0
    
    def test_frontend_accessible(self):
        """Test frontend is accessible."""
        response = requests.get(FRONTEND_URL)
        assert response.status_code == 200
        assert b"Biomedical Search" in response.content or b"search" in response.content.lower()


class TestSearchFunctionality:
    """Test search functionality end-to-end."""
    
    @pytest.fixture
    def search_queries(self) -> List[str]:
        """Sample search queries."""
        return [
            "COVID-19 treatment",
            "diabetes management",
            "cancer immunotherapy",
            "Alzheimer disease",
            "HIV antiretroviral therapy"
        ]
    
    def test_basic_search(self, search_queries):
        """Test basic search functionality."""
        for query in search_queries:
            response = requests.post(
                f"{API_BASE_URL}/search",
                json={
                    "query": query,
                    "index": "both",
                    "max_results": 10,
                    "alpha": 0.5,
                    "use_reranking": False
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "results" in data
            assert "total_results" in data
            assert "query" in data
            assert data["query"] == query
            assert len(data["results"]) > 0
            
            # Verify result structure
            for result in data["results"]:
                assert "id" in result
                assert "title" in result
                assert "score" in result
                assert "source" in result
                assert result["source"] in ["pubmed", "clinical_trials"]
    
    def test_search_with_reranking(self):
        """Test search with cross-encoder reranking."""
        response = requests.post(
            f"{API_BASE_URL}/search",
            json={
                "query": "COVID-19 vaccine efficacy",
                "index": "both",
                "max_results": 20,
                "alpha": 0.5,
                "use_reranking": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) > 0
        
        # Verify scores are in descending order
        scores = [r["score"] for r in data["results"]]
        assert scores == sorted(scores, reverse=True)
    
    def test_search_different_sources(self):
        """Test searching different sources."""
        sources = ["pubmed", "clinical_trials", "both"]
        
        for source in sources:
            response = requests.post(
                f"{API_BASE_URL}/search",
                json={
                    "query": "diabetes",
                    "index": source,
                    "max_results": 10,
                    "alpha": 0.5,
                    "use_reranking": False
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["results"]) > 0
            
            # Verify source filtering
            if source == "pubmed":
                assert all(r["source"] == "pubmed" for r in data["results"])
            elif source == "clinical_trials":
                assert all(r["source"] == "clinical_trials" for r in data["results"])
    
    def test_search_alpha_parameter(self):
        """Test alpha parameter (keyword vs semantic balance)."""
        query = "hypertension treatment"
        
        for alpha in [0.0, 0.5, 1.0]:
            response = requests.post(
                f"{API_BASE_URL}/search",
                json={
                    "query": query,
                    "index": "both",
                    "max_results": 10,
                    "alpha": alpha,
                    "use_reranking": False
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["results"]) > 0


class TestQuestionAnswering:
    """Test question answering functionality."""
    
    @pytest.fixture
    def test_questions(self) -> List[Dict]:
        """Sample questions for testing."""
        return [
            {
                "question": "What are the symptoms of COVID-19?",
                "index": "pubmed",
                "expected_keywords": ["symptom", "fever", "cough"]
            },
            {
                "question": "How is diabetes treated?",
                "index": "both",
                "expected_keywords": ["treatment", "insulin", "medication"]
            },
            {
                "question": "What causes Alzheimer's disease?",
                "index": "pubmed",
                "expected_keywords": ["cause", "brain", "protein"]
            }
        ]
    
    def test_basic_qa(self, test_questions):
        """Test basic question answering."""
        for test_case in test_questions:
            response = requests.post(
                f"{API_BASE_URL}/question",
                json={
                    "question": test_case["question"],
                    "index": test_case["index"],
                    "max_answers": 3,
                    "min_confidence": 0.01
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "answers" in data
            assert "question" in data
            assert data["question"] == test_case["question"]
            
            # Should have at least one answer
            if len(data["answers"]) > 0:
                answer = data["answers"][0]
                assert "answer" in answer or "text" in answer
                assert "confidence" in answer
                assert "source_title" in answer or "source_document" in answer
                # Context may be None in some cases
    
    def test_qa_multiple_answers(self):
        """Test retrieving multiple answers."""
        for num_answers in [1, 3, 5]:
            response = requests.post(
                f"{API_BASE_URL}/question",
                json={
                    "question": "What is hypertension?",
                    "index": "both",
                    "max_answers": num_answers,
                    "min_confidence": 0.01
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Should return at most the requested number of answers
            assert len(data["answers"]) <= num_answers


class TestPerformance:
    """Test system performance."""
    
    def test_search_response_time(self):
        """Test search response time is acceptable."""
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/search",
            json={
                "query": "cancer treatment",
                "index": "both",
                "max_results": 20,
                "alpha": 0.5,
                "use_reranking": False
            }
        )
        
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed_time < 5.0  # Should respond within 5 seconds
        
        data = response.json()
        assert "search_time_ms" in data
    
    def test_qa_response_time(self):
        """Test QA response time is acceptable."""
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/question",
            json={
                "question": "What are the risk factors for stroke?",
                "index": "both",
                "max_answers": 3,
                "min_confidence": 0.01
            }
        )
        
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed_time < 10.0  # Should respond within 10 seconds
    
    def test_concurrent_requests(self):
        """Test handling concurrent requests."""
        import concurrent.futures
        
        def make_search_request(query_id: int):
            response = requests.post(
                f"{API_BASE_URL}/search",
                json={
                    "query": f"test query {query_id}",
                    "index": "both",
                    "max_results": 10,
                    "alpha": 0.5,
                    "use_reranking": False
                }
            )
            return response.status_code
        
        # Test 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_search_request, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert all(status == 200 for status in results)


class TestErrorHandling:
    """Test error handling."""
    
    def test_empty_query(self):
        """Test handling of empty query."""
        response = requests.post(
            f"{API_BASE_URL}/search",
            json={
                "query": "",
                "index": "both",
                "max_results": 10,
                "alpha": 0.5,
                "use_reranking": False
            }
        )
        
        # Should handle gracefully (might return 400 or 200 with no results)
        assert response.status_code in [200, 400, 422]
    
    def test_invalid_index(self):
        """Test handling of invalid index."""
        response = requests.post(
            f"{API_BASE_URL}/search",
            json={
                "query": "test",
                "index": "invalid_index",
                "max_results": 10,
                "alpha": 0.5,
                "use_reranking": False
            }
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]
    
    def test_invalid_max_results(self):
        """Test handling of invalid max_results."""
        response = requests.post(
            f"{API_BASE_URL}/search",
            json={
                "query": "test",
                "index": "both",
                "max_results": 1000,  # Beyond limit
                "alpha": 0.5,
                "use_reranking": False
            }
        )
        
        # Should return validation error
        assert response.status_code == 422


class TestDataQuality:
    """Test data quality and consistency."""
    
    def test_document_structure(self):
        """Test that indexed documents have proper structure."""
        response = requests.post(
            f"{API_BASE_URL}/search",
            json={
                "query": "diabetes",
                "index": "both",
                "max_results": 5,
                "alpha": 0.5,
                "use_reranking": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for result in data["results"]:
            # Required fields
            assert result["title"]
            assert result["id"]
            assert result["source"] in ["pubmed", "clinical_trials"]
            
            # Metadata should exist
            assert "metadata" in result
            
            # Source-specific fields
            if result["source"] == "pubmed":
                assert "pmid" in result["metadata"] or result["metadata"].get("pmid")
            elif result["source"] == "clinical_trials":
                assert "nct_id" in result["metadata"] or result["metadata"].get("nct_id")


if __name__ == "__main__":
    print("=" * 80)
    print("INTEGRATION TEST SUITE")
    print("=" * 80)
    print("\nMake sure the following are running:")
    print("1. Elasticsearch on port 9201")
    print("2. API server on port 8000")
    print("3. Frontend on port 8080")
    print("\nRunning tests with pytest...")
    print("=" * 80)
    
    pytest.main([__file__, "-v", "--tb=short"])
