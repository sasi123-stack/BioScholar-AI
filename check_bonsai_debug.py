from elasticsearch import Elasticsearch
import time

# Credentials from user
bonsai_url = "https://0204784e62:38aa998d6c5c2891232c@assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net"

def check_connection():
    try:
        print(f"Connecting to: {bonsai_url}")
        # Try without sniffing or complex configs first
        es = Elasticsearch([bonsai_url], verify_certs=True, request_timeout=30)
        
        print("Pinging...")
        if es.ping():
            print("✅ Successfully connected to Bonsai Elasticsearch!")
            info = es.info()
            print(f"Cluster Name: {info['cluster_name']}")
            print(f"Version: {info['version']['number']}")
        else:
            print("❌ Ping returned False. Connection failed.")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    check_connection()
