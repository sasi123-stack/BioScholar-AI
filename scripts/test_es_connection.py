
from elasticsearch import Elasticsearch

host = "assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net"
user = "0204784e62"
password = "38aa998d6c5c2891232c"

print(f"Connecting to {host}...")

try:
    es = Elasticsearch(
        [f"https://{host}:443"],
        basic_auth=(user, password),
        verify_certs=True
    )
    
    if es.ping():
        print("✅ SUCCESS: Connected to Bonsai Elasticsearch!")
        print(es.info())
    else:
        print("❌ FAILED: Ping returned False. Credentials or Host might be wrong.")
        
except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")
