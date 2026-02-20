from elasticsearch import Elasticsearch
import time
import requests

# Credentials from user
bonsai_url = "https://0204784e62:38aa998d6c5c2891232c@assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net"

def check_connection():
    try:
        print(f"Connecting to: {bonsai_url}")
        
        # Test 1: Requests
        print("Testing with requests...")
        try:
            r = requests.get(bonsai_url, timeout=10)
            print(f"Requests Status: {r.status_code}")
            print(f"Requests Content: {r.text[:200]}")
        except Exception as req_e:
            print(f"Requests failed: {req_e}")

        # Test 2: Elasticsearch client
        print("\nTesting with Elasticsearch client...")
        es = Elasticsearch(
            [bonsai_url]
        )
        
        if es.ping():
            print("✅ Successfully connected to Bonsai Elasticsearch!")
            info = es.info()
            print(f"Cluster Name: {info['cluster_name']}")
        else:
            print("❌ Ping returned False. Connection failed.")

    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    check_connection()
