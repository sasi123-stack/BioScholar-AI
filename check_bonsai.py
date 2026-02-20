from elasticsearch import Elasticsearch

# Credentials from user
bonsai_url = "https://0204784e62:38aa998d6c5c2891232c@assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net"

def check_connection():
    try:
        print(f"Connecting to: {bonsai_url}")
        es = Elasticsearch([bonsai_url])
        if es.ping():
            print("✅ Successfully connected to Bonsai Elasticsearch!")
            print(es.info())
        else:
            print("❌ Could not ping Bonsai Elasticsearch.")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    check_connection()
