import requests
import json

url = "https://sasidhara123-biomed-scholar-api.hf.space/api/v1/search"
payload = {
    "query": "chemotherapy",
    "index": "both",
    "max_results": 5,
    "alpha": 0.0, # alpha 0.0 means semantic focused (1.0 semantic weight in hybrid_search code logic...)
    # Wait, check hybrid_search.py logic for alpha.
    # line 284: combined_score = alpha * kw_score + (1 - alpha) * sem_score
    # So alpha=0.0 means 100% semantic score.
    "use_reranking": False,
    "sort_by": "relevance"
}

print(f"Testing Semantic Search at: {url}")
try:
    response = requests.post(url, json=payload, timeout=60)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Found {len(data.get('results', []))} results.")
        for r in data.get('results', []):
            print(f"- {r['title']} (Score: {r['score']})")
    else:
        print(f"Failed: {response.text}")
except Exception as e:
    print(f"Error: {e}")
