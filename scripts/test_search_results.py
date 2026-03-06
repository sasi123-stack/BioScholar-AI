import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.indexing import ElasticsearchClient
from src.utils.logger import get_logger

logger = get_logger(__name__)

def test_search():
    es_client = ElasticsearchClient()
    client = es_client.client
    
    queries = ["Alzheimer's", "Cancer Immunotherapy"]
    
    for query in queries:
        print(f"\n🔍 Searching for: {query}")
        
        # Keyword search
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title", "abstract", "conditions"]
                }
            },
            "size": 3
        }
        
        try:
            res = client.search(index="clinical_trials", body=body)
            hits = res['hits']['hits']
            print(f"✅ Found {res['hits']['total']['value']} results.")
            for hit in hits:
                source = hit['_source']
                print(f"- [{source.get('id')}] {source.get('title')[:100]}...")
        except Exception as e:
            print(f"❌ Error searching for '{query}': {e}")

if __name__ == "__main__":
    test_search()
