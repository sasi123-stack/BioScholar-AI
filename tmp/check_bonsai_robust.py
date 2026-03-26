from elasticsearch import Elasticsearch
import sys

# Credentials from user
bonsai_url = "https://0204784e62:38aa998d6c5c2891232c@assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net"

def check_connection():
    try:
        print(f"Connecting to: {bonsai_url.split('@')[1]}") # Hide credentials in log
        es = Elasticsearch([bonsai_url])
        if es.ping():
            print("SUCCESS: Successfully connected to Bonsai Elasticsearch!")
            print(es.info())
            
            # Check indices
            print("\nIndices:")
            print(es.cat.indices(v=True))
        else:
            print("FAILURE: Could not ping Bonsai Elasticsearch.")
    except Exception as e:
        print(f"ERROR: Connection failed: {str(e)}")

if __name__ == "__main__":
    check_connection()
