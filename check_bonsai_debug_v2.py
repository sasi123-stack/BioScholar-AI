from elasticsearch import Elasticsearch
import time
import ssl

# Credentials from user
bonsai_url = "https://0204784e62:38aa998d6c5c2891232c@assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net"

def check_connection():
    try:
        print(f"Connecting to: {bonsai_url}")
        
        # Explicitly configure SSL context and timeout
        es = Elasticsearch(
            [bonsai_url],
            verify_certs=True,
            request_timeout=30,
            use_ssl=True
        )
        
        print("Pinging...")
        if es.ping():
            print("✅ Successfully connected to Bonsai Elasticsearch!")
            try:
                info = es.info()
                print(f"Cluster Name: {info['cluster_name']}")
                print(f"Version: {info['version']['number']}")
            except Exception as e:
                print(f"Ping successful, but info failed: {e}")
        else:
            print("❌ Ping returned False. Connection failed.")
            print("Debugging: Checking if we can reach with requests library...")
            import requests
            try:
                r = requests.get(bonsai_url, timeout=10)
                print(f"Requests Status: {r.status_code}")
                print(f"Requests Content: {r.text[:200]}")
            except Exception as req_e:
                print(f"Requests failed too: {req_e}")

    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    check_connection()
