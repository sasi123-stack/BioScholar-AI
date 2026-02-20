
import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
ES_HOST = "assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net"
ES_USER = "0204784e62"
ES_PASS = "38aa998d6c5c2891232c"
ES_BASE_URL = f"https://{ES_HOST}:443"


def make_es_request(method, path, data=None):
    url = f"{ES_BASE_URL}/{path}"
    headers = {"Content-Type": "application/json"}
    auth = (ES_USER, ES_PASS)
    
    resp = None
    try:
        if method == "GET":
            resp = requests.get(url, auth=auth, headers=headers)
        elif method == "PUT":
            resp = requests.put(url, auth=auth, headers=headers, json=data)
        elif method == "HEAD":
            resp = requests.head(url, auth=auth, headers=headers)
    except Exception as e:
        logger.error(f"Request failed: {e}")
        
    return resp

def create_missing_index():
    index_name = "clinical_trials"
    
    # Check if exists
    resp = make_es_request("HEAD", index_name)
    if resp.status_code == 200:
        logger.info(f"Index '{index_name}' already exists.")
        return

    # Create Index
    mapping = {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "title": {"type": "text"},
                "abstract": {"type": "text"},
                "source": {"type": "keyword"},
                "metadata": {"type": "object"},
                "embedding": {"type": "dense_vector", "dims": 768, "index": False}
            }
        }
    }

    resp = make_es_request("PUT", index_name, mapping)
    if resp.status_code == 200:
        logger.info(f"✅ Successfully created index: {index_name}")
    else:
        logger.error(f"❌ Failed to create index: {resp.text}")

if __name__ == "__main__":
    create_missing_index()
