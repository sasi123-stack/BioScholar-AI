import sys
import os
sys.path.append("d:/MTech 2nd Year/BioMedScholar AI")

from app_minimal import fallback_search_entrez

def test():
    query = "cancer"
    print(f"Testing Entrez Fallback for query: {query}")
    try:
        results = fallback_search_entrez(query, max_results=5)
        print(f"SUCCESS: Found {len(results)} results via Entrez.")
        for r in results:
            print(f"- {r.get('title')} ({r.get('id')})")
    except Exception as e:
        print(f"FAILURE: Fallback failed: {e}")

if __name__ == "__main__":
    test()
