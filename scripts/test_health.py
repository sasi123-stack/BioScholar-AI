"""
Simple API health check test.
"""

import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

print("Testing API Health Check...")
print(f"URL: {BASE_URL}/health\n")

try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ API is healthy!")
        print(f"   Status: {data['status']}")
        print(f"   Elasticsearch: {'✅' if data['elasticsearch'] else '❌'}")
        print(f"   Models Loaded: {'✅' if data['models_loaded'] else '❌'}")
        print(f"   Version: {data['version']}")
    else:
        print(f"\n❌ Health check failed: {response.text}")

except requests.exceptions.ConnectionError:
    print("\n❌ Could not connect to API. Is the server running?")
    print("Start server with: python -m uvicorn src.api.app:app --reload")
except Exception as e:
    print(f"\n❌ Error: {e}")
