from opensearchpy import OpenSearch
import requests

# Credentials from config
ES_HOST = "assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net"
ES_USER = "0204784e62"
ES_PASS = "38aa998d6c5c2891232c"
ES_URL = f"https://{ES_USER}:{ES_PASS}@{ES_HOST}:443"

def debug_scripts():
    try:
        client = OpenSearch([ES_URL], use_ssl=True, verify_certs=True)
        info = client.info()
        print(f"Version: {info['version']['number']}")
        print(f"Distribution: {info['version'].get('distribution', 'elasticsearch')}")
        
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
        try:
            resp = client.search(index="clinical_trials", body=test_query)
            print("✅ cosineSimilarity works!")
        except Exception as e:
            print(f"❌ cosineSimilarity failed: {e}")
            
            # Try manual dot product as fallback test
            print("Testing manual dot product script...")
            manual_script = {
                "size": 1,
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": """
                                double dot = 0;
                                if (doc.containsKey('embedding') && doc['embedding'].size() > 0) {
                                    for (int i = 0; i < params.query_vector.length; i++) {
                                        dot += params.query_vector[i] * doc['embedding'][i];
                                    }
                                }
                                return dot + 1.0;
                            """,
                            "params": {"query_vector": [0.1] * 768}
                        }
                    }
                }
            }
            try:
                resp = client.search(index="clinical_trials", body=manual_script)
                print("✅ Manual dot product works!")
            except Exception as e2:
                print(f"❌ Manual dot product failed: {e2}")

    except Exception as e:
        print(f"General error: {e}")

if __name__ == "__main__":
    debug_scripts()
