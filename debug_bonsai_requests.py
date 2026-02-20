import requests
import json

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
            print("✅ cosineSimilarity works!")
        else:
            print(f"❌ cosineSimilarity failed ({resp.status_code}): {resp.text}")
            
            # Try dotProduct as alternative (ES 8+) or use manual dot product
            print("Testing dotProduct script...")
            dot_query = {
                "size": 1,
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "dotProduct(params.query_vector, 'embedding') + 1.0",
                            "params": {"query_vector": [0.1] * 768}
                        }
                    }
                }
            }
            resp = requests.post(f"{ES_URL}/clinical_trials/_search", auth=auth, json=dot_query)
            if resp.status_code == 200:
                print("✅ dotProduct works!")
            else:
                print(f"❌ dotProduct failed ({resp.status_code}): {resp.text}")

    except Exception as e:
        print(f"General error: {e}")

if __name__ == "__main__":
    debug_scripts()
