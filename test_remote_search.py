import requests
import json

url = "https://sasidhara123-biomed-scholar-api.hf.space/api/v1/search"
payload = {
    "query": "cancer immunotherapy",
    "index": "clinical_trials",
    "max_results": 5,
    "alpha": 0.5,
    "use_reranking": True,
    "sort_by": "relevance",
    "date_from": None,
    "date_to": None
}

print(f"Testing URL: {url}")
try:
    response = requests.post(url, json=payload, timeout=60)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total results found: {data.get('total_results', 0)}")
        for i, result in enumerate(data.get('results', []), 1):
            print(f"{i}. [{result.get('source')}] {result.get('title')}")
    else:
        print("Test failed.")
except Exception as e:
    print(f"Error: {e}")
