
import requests
import json

def test_search():
    url = "http://localhost:8000/api/v1/search"
    payload = {
        "query": "cancer",
        "index": "both",
        "max_results": 20
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            print(f"Total Results: {data.get('total_results', 0)}")
            results = data.get('results', [])
            sources = {}
            for r in results:
                s = r.get('source', 'unknown')
                sources[s] = sources.get(s, 0) + 1
            print(f"Sources found: {sources}")
            if results:
                print(f"First result source: {results[0].get('source')}")
                print(f"First result title: {results[0].get('title')[:50]}...")
        else:
            print(f"Error: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    test_search()
