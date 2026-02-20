
import requests

API_URL = "https://sasidhara123-biomed-scholar-api.hf.space/api/v1"

print(f"Checking API: {API_URL}")

try:
    # 1. Health Check
    print("Testing /health ...")
    resp = requests.get(f"{API_URL}/health")
    print(f"Status: {resp.status_code}")
    print(f"Payload: {resp.text}")

    # 2. Search (Correct POST request)
    print("\nTesting /search (cancer)...")
    payload = {
        "query": "cancer",
        "max_results": 5,
        "index": "both",
        "use_reranking": False
    }
    resp = requests.post(f"{API_URL}/search", json=payload)
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Success! Found {data.get('total_results')} results.")
        results = data.get('results', [])
        if results:
            print(f"Sample: {results[0].get('title')}")
    else:
        print(f"❌ Failed: {resp.status_code}")
        print(f"Error: {resp.text}")

except Exception as e:
    print(f"❌ Connection Error: {e}")
