from src.search_engine.hybrid_search import HybridSearchEngine
import time

try:
    engine = HybridSearchEngine()
    print("Connecting to Elasticsearch...")
    
    # Check counts
    indices = ["pubmed_articles", "clinical_trials"]
    total = 0
    for index in indices:
        try:
            count = engine.es_client.client.count(index=index)["count"]
            print(f"Index '{index}': {count} documents")
            total += count
        except Exception as e:
            print(f"Index '{index}': Error - {e}")

    print(f"Total documents: {total}")
    
except Exception as e:
    print(f"Failed to connect: {e}")
