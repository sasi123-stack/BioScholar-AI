import requests
import json

url = "http://localhost:8000/api/v1/search"
payload = {
    "query": "covid",
    "index": "both",
    "max_results": 5,
    "alpha": 0.5,
    "use_reranking": False
}

try:
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total results found: {data.get('total_results', 0)}")
    for i, result in enumerate(data.get('results', []), 1):
        print(f"{i}. {result.get('title')}")
except Exception as e:
    print(f"Error: {e}")
