
import os
import sys
import logging
import requests
import json

# Add project root path
sys.path.append(os.getcwd())
from src.data_pipeline.pubmed_fetcher import PubMedFetcher

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
        elif method == "DELETE":
            resp = requests.delete(url, auth=auth, headers=headers)
        elif method == "POST":
            resp = requests.post(url, auth=auth, headers=headers, json=data)
        elif method == "HEAD":
            resp = requests.head(url, auth=auth, headers=headers)
    except Exception as e:
        logger.error(f"Request failed: {e}")
        
    return resp

def ingest_data():
    """Ingest REAL data using raw Requests."""
    
    logger.info(f"Connecting to Cloud Elasticsearch...")

    # 1. Test Connection
    resp = make_es_request("GET", "")
    if resp.status_code == 200:
        logger.info(f"✅ Connected! Cluster: {resp.json().get('cluster_name')}")
    else:
        logger.error(f"❌ Failed to connect: {resp.text}")
        return

    # 2. Create Index
    index_name = "pubmed_articles"
    # We will delete and recreate to ensure clean slate
    resp = make_es_request("HEAD", index_name)
    if resp.status_code == 200:
        logger.info(f"Index '{index_name}' exists. Deleting...")
        make_es_request("DELETE", index_name)

    # Simplified mapping for cloud (Text only)
    mapping = {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "title": {"type": "text"},
                "abstract": {"type": "text"},
                "authors": {"type": "text"},
                "publication_year": {"type": "keyword"},
                "source": {"type": "keyword"},
                "metadata": {"type": "object"},
                "score": {"type": "float"},
                "embedding": {"type": "dense_vector", "dims": 768, "index": False} # Disable indexing for now to save space/time
            }
        }
    }

    resp = make_es_request("PUT", index_name, mapping)
    if resp.status_code == 200:
        logger.info(f"✅ Created index: {index_name}")
    else:
        logger.error(f"❌ Failed to create index: {resp.text}")

    # 3. Fetch Real Data
    logger.info("Fetching articles from PubMed...")
    fetcher = PubMedFetcher(email="student@university.edu")
    
    queries = [
        "cancer immunotherapy",
        "CRISPR gene editing",
        "covid-19 vaccine side effects",
        "alzheimers treatment",
        "diabetes management",
        "artificial intelligence in medicine",
        "climate change health impact"
    ]
    
    total_indexed = 0
    
    for query in queries:
        logger.info(f"--- Processing query: '{query}' ---")
        articles = fetcher.search_and_fetch(query, max_results=30) # Fetch 30 per topic
        
        if articles:
            success_count = 0
            for doc in articles:
                # Add dummy embedding
                doc['embedding'] = [0.0] * 768 
                
                # Format for ES
                # Ensure ID is string
                doc_id = str(doc.get('pmid') or doc.get('id', ''))
                if not doc_id: continue
                
                doc['id'] = doc_id
                doc['source'] = 'pubmed'
                doc['metadata'] = {
                    'journal': doc.get('journal'),
                    'publication_date': doc.get('publication_date'),
                    'authors': doc.get('authors', [])
                }
                
                resp = make_es_request("PUT", f"{index_name}/_doc/{doc_id}", doc)
                if resp and resp.status_code in [200, 201]:
                     success_count += 1
                     print(".", end="", flush=True)
            
            logger.info(f"\nIndexed {success_count} articles for '{query}'")
            total_indexed += success_count
        else:
            logger.warning(f"No articles found for '{query}'")

    logger.info(f"\n🎉 SUCCESS! Indexed {total_indexed} documents.")
    logger.info("Go to your website and refresh!")

if __name__ == "__main__":
    ingest_data()
