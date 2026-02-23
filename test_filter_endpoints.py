import requests
import json
from datetime import datetime
import sys

API_BASE = "https://sasidhara123-biomed-scholar-api.hf.space/api/v1"

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_health():
    print_section("TEST 1: HEALTH CHECK ENDPOINT")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=15)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response:\n{json.dumps(data, indent=2)}")
        return data
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        return None

def test_statistics():
    print_section("TEST 2: STATISTICS ENDPOINT")
    try:
        response = requests.get(f"{API_BASE}/statistics", timeout=15)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response:\n{json.dumps(data, indent=2)}")
        return data
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        return None

def test_search_basic():
    print_section("TEST 3: BASIC SEARCH (No Filters)")
    query = "diabetes treatment"
    payload = {
        "query": query,
        "index": "both",
        "max_results": 10,
        "alpha": 0.5,
        "use_reranking": True,
        "sort_by": "relevance"
    }
    try:
        response = requests.post(f"{API_BASE}/search", json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Total Results: {data.get('total_results')}")
        print(f"Search Time: {data.get('search_time_ms')}ms")
        print(f"Results Count: {len(data.get('results', []))}")
        if data.get('results'):
            print(f"\nFirst Result:\n{json.dumps(data['results'][0], indent=2)}")
        return data
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        return None

def test_search_pubmed_only():
    print_section("TEST 4: SEARCH - PubMed Source Only")
    query = "COVID-19 vaccine"
    payload = {
        "query": query,
        "index": "pubmed",
        "max_results": 5,
        "alpha": 0.2,
        "use_reranking": True,
        "sort_by": "date_desc"
    }
    try:
        response = requests.post(f"{API_BASE}/search", json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Total Results: {data.get('total_results')}")
        print(f"Results Count: {len(data.get('results', []))}")
        if data.get('results'):
            for i, result in enumerate(data['results'][:2]):
                print(f"\nResult {i+1}:")
                print(f"  Title: {result.get('title')[:80]}")
                print(f"  Source: {result.get('source')}")
                print(f"  Score: {result.get('score')}")
                meta = result.get('metadata', {})
                print(f"  Date: {meta.get('publication_date')}")
        return data
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        return None

def test_search_clinical_trials():
    print_section("TEST 5: SEARCH - Clinical Trials Only")
    query = "cancer immunotherapy"
    payload = {
        "query": query,
        "index": "clinical_trials",
        "max_results": 5,
        "alpha": 0.8,
        "use_reranking": False,
        "sort_by": "relevance"
    }
    try:
        response = requests.post(f"{API_BASE}/search", json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Total Results: {data.get('total_results')}")
        print(f"Results Count: {len(data.get('results', []))}")
        if data.get('results'):
            for i, result in enumerate(data['results'][:2]):
                print(f"\nResult {i+1}:")
                print(f"  Title: {result.get('title')[:80]}")
                print(f"  Source: {result.get('source')}")
                meta = result.get('metadata', {})
                print(f"  NCT ID: {meta.get('nct_id')}")
        return data
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        return None

def test_search_keyword_mode():
    print_section("TEST 6: SEARCH - Keyword Mode (Alpha=0)")
    query = "hypertension treatment"
    payload = {
        "query": query,
        "index": "pubmed",
        "max_results": 5,
        "alpha": 0.0,
        "use_reranking": False,
        "sort_by": "relevance"
    }
    try:
        response = requests.post(f"{API_BASE}/search", json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Total Results: {data.get('total_results')}")
        return data
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        return None

def test_search_semantic_mode():
    print_section("TEST 7: SEARCH - Semantic Mode (Alpha=1.0)")
    query = "myocardial infarction recovery"
    payload = {
        "query": query,
        "index": "pubmed",
        "max_results": 5,
        "alpha": 1.0,
        "use_reranking": True,
        "sort_by": "relevance"
    }
    try:
        response = requests.post(f"{API_BASE}/search", json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Total Results: {data.get('total_results')}")
        return data
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        return None

def test_search_date_sorted():
    print_section("TEST 8: SEARCH - Date Sorted (Newest First)")
    query = "artificial intelligence medicine"
    payload = {
        "query": query,
        "index": "pubmed",
        "max_results": 5,
        "alpha": 0.5,
        "use_reranking": True,
        "sort_by": "date_desc"
    }
    try:
        response = requests.post(f"{API_BASE}/search", json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Total Results: {data.get('total_results')}")
        if data.get('results'):
            for i, result in enumerate(data['results'][:3]):
                meta = result.get('metadata', {})
                print(f"\nResult {i+1}:")
                print(f"  Date: {meta.get('publication_date')}")
                print(f"  Title: {result.get('title')[:80]}")
        return data
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        return None

def test_question_answering():
    print_section("TEST 9: QUESTION-ANSWERING ENDPOINT")
    question = "What are the side effects of metformin?"
    payload = {
        "question": question,
        "index": "pubmed",
        "max_answers": 3,
        "max_passages": 5,
        "min_confidence": 0.3
    }
    try:
        response = requests.post(f"{API_BASE}/question", json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Question: {data.get('question')}")
        print(f"Status: {data.get('status')}")
        print(f"Answers Count: {len(data.get('answers', []))}")
        print(f"QA Time: {data.get('qa_time_ms')}ms")
        if data.get('answers'):
            for i, answer in enumerate(data['answers'][:2]):
                print(f"\nAnswer {i+1}:")
                print(f"  Text: {answer.get('answer')[:100]}")
                conf = answer.get('confidence', 0)
                print(f"  Confidence: {conf:.2f} ({answer.get('confidence_level')})")
                print(f"  Source: {answer.get('source_title')[:60]}")
        return data
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        return None

def test_empty_query():
    print_section("TEST 10: SEARCH - Empty Query")
    payload = {
        "query": "",
        "index": "both",
        "max_results": 10,
        "alpha": 0.5,
        "use_reranking": True,
        "sort_by": "relevance"
    }
    try:
        response = requests.post(f"{API_BASE}/search", json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return data
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        return None

def test_special_characters():
    print_section("TEST 11: SEARCH - Special Characters")
    query = "COVID-19 mRNA vaccine efficacy"
    payload = {
        "query": query,
        "index": "pubmed",
        "max_results": 5,
        "alpha": 0.5,
        "use_reranking": True,
        "sort_by": "relevance"
    }
    try:
        response = requests.post(f"{API_BASE}/search", json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Total Results: {data.get('total_results')}")
        return data
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        return None

if __name__ == "__main__":
    print(f"\n\nFull Research Filters & Backend Response Testing")
    print(f"API Base: {API_BASE}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run all tests
    test_health()
    test_statistics()
    test_search_basic()
    test_search_pubmed_only()
    test_search_clinical_trials()
    test_search_keyword_mode()
    test_search_semantic_mode()
    test_search_date_sorted()
    test_question_answering()
    test_empty_query()
    test_special_characters()

    print(f"\n\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "="*70)
