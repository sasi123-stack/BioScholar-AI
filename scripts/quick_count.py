
import requests

# --- CONFIGURATION ---
ES_HOST = "assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net"
ES_USER = "0204784e62"
ES_PASS = "38aa998d6c5c2891232c"
ES_BASE_URL = f"https://{ES_HOST}:443"

def check_counts():
    indices = ["pubmed_articles", "clinical_trials"]
    auth = (ES_USER, ES_PASS)
    
    for index in indices:
        url = f"{ES_BASE_URL}/{index}/_count"
        try:
            resp = requests.get(url, auth=auth)
            if resp.status_code == 200:
                count = resp.json().get("count", 0)
                print(f"Index '{index}': {count} documents")
            else:
                print(f"Index '{index}': Error {resp.status_code}")
        except Exception as e:
            print(f"Index '{index}': Exception {e}")

if __name__ == "__main__":
    check_counts()
