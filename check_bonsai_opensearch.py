from opensearchpy import OpenSearch
import time

# Credentials from user
bonsai_url = "https://0204784e62:38aa998d6c5c2891232c@assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net"

def check_connection():
    try:
        print(f"Connecting to: {bonsai_url}")
        # Bonsai often provides OpenSearch under the hood now, which works slightly differently
        client = OpenSearch([bonsai_url], use_ssl=True, verify_certs=True)
        
        print("Pinging...")
        if client.ping():
            print("✅ Successfully connected to Bonsai (OpenSearch)!")
            info = client.info()
            print(f"Cluster Name: {info['cluster_name']}")
            print(f"Version: {info['version']['number']}")
            print("Distribution: " + info['version'].get('distribution', 'elasticsearch'))
        else:
            print("❌ Ping returned False. Connection failed.")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    check_connection()
