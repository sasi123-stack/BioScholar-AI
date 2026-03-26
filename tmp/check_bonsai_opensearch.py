from opensearchpy import OpenSearch
import sys

ES_HOST = "assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net"
ES_USER = "0204784e62"
ES_PASS = "38aa998d6c5c2891232c"

def check_connection():
    try:
        print(f"Connecting to OpenSearch/Bonsai: {ES_HOST}")
        client = OpenSearch(
            hosts=[f"https://{ES_USER}:{ES_PASS}@{ES_HOST}:443"],
            use_ssl=True, verify_certs=True,
            timeout=10
        )
        
        if client.ping():
            print("SUCCESS: Connected to Bonsai via OpenSearch!")
            print(client.info())
        else:
            print("FAILURE: Ping failed via OpenSearch.")
    except Exception as e:
        print(f"ERROR: OpenSearch connection failed: {str(e)}")

if __name__ == "__main__":
    check_connection()
