import requests
import json
import sys

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Credentials from config
ES_HOST = "assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net"
ES_USER = "0204784e62"
ES_PASS = "38aa998d6c5c2891232c"
ES_URL = f"https://{ES_HOST}:443"

def debug_scripts():
    auth = (ES_USER, ES_PASS)
    try:
        resp = requests.get(ES_URL, auth=auth)
        info = resp.json()
        print(f"Version: {info['version']['number']}")
        dist = info['version'].get('distribution', 'elasticsearch')
        print(f"Distribution: {dist}")
        
        # Test a simple script score with cosineSimilarity
        test_query = {
            "size": 1,
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": [0.1] * 768}
                    }
                }
            }
        }
        
        print("Testing cosineSimilarity script...")
        resp = requests.post(f"{ES_URL}/clinical_trials/_search", auth=auth, json=test_query)
        if resp.status_code == 200:
            print("FOUND: cosineSimilarity works!")
        else:
            print(f"FAILED: cosineSimilarity failed ({resp.status_code}): {resp.text}")
            
            # Try manual dot product
            print("Testing manual dot product script...")
            manual_script = {
                "size": 1,
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "double dot = 0; if (doc.containsKey('embedding') && doc['embedding'].size() > 0) { for (int i = 0; i < params.query_vector.length; i++) { dot += params.query_vector[i] * doc['embedding'][i]; } } return dot + 1.0;",
                            "params": {"query_vector": [0.1] * 768}
                        }
                    }
                }
            }
            resp = requests.post(f"{ES_URL}/clinical_trials/_search", auth=auth, json=manual_script)
            if resp.status_code == 200:
                print("FOUND: Manual dot product works!")
            else:
                print(f"FAILED: Manual dot product failed ({resp.status_code}): {resp.text}")

    except Exception as e:
        print(f"General error: {e}")

if __name__ == "__main__":
    debug_scripts()
