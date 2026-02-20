
from opensearchpy import OpenSearch, helpers
import requests
import json
import time
import xml.etree.ElementTree as ET
from src.utils.logger import logger

# --- CONFIGURATION ---
ES_HOST = "assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net"
ES_USER = "0204784e62"
ES_PASS = "38aa998d6c5c2891232c"
ES_URL = f"https://{ES_USER}:{ES_PASS}@{ES_HOST}:443"

PUBMED_API_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def get_opensearch_client():
    """Create and return an OpenSearch client."""
    return OpenSearch(
        hosts=[ES_URL],
        use_ssl=True,
        verify_certs=True,
        ssl_assert_hostname=False,
        ssl_show_warn=False
    )

def fetch_pubmed_ids(query, max_results=20):
    """Search PubMed for IDs."""
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
    }
    try:
        resp = requests.get(f"{PUBMED_API_BASE}/esearch.fcgi", params=params)
        data = resp.json()
        return data["esearchresult"]["idlist"]
    except Exception as e:
        print(f"PubMed Search Error: {e}")
        return []

def fetch_pubmed_details(pmids):
    """Fetch details for a list of PMIDs."""
    if not pmids:
        return []
    
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
    }
    
    try:
        resp = requests.post(f"{PUBMED_API_BASE}/efetch.fcgi", data=params)
        return parse_pubmed_xml(resp.text)
    except Exception as e:
        print(f"PubMed Fetch Error: {e}")
        return []

def parse_pubmed_xml(xml_text):
    """Parse PubMed XML into dictionaries."""
    articles = []
    try:
        root = ET.fromstring(xml_text)
        for article in root.findall(".//PubmedArticle"):
            data = {}
            
            # PMID
            pmid = article.find(".//PMID")
            data["id"] = pmid.text if pmid is not None else None
            if not data["id"]: continue

            # Title
            title = article.find(".//ArticleTitle")
            data["title"] = title.text if title is not None else "No Title"

            # Abstract
            abstract_parts = [elem.text for elem in article.findall(".//AbstractText") if elem.text]
            data["abstract"] = " ".join(abstract_parts) if abstract_parts else "No Abstract"

            # Year
            pub_date = article.find(".//PubDate/Year")
            if pub_date is None:
                 pub_date = article.find(".//PubDate/MedlineDate")
                 
            data["publication_year"] = pub_date.text[:4] if pub_date is not None and pub_date.text else "2024"
            
            # Authors
            authors_list = []
            for author in article.findall(".//Author"):
                last = author.find("LastName")
                initials = author.find("Initials")
                if last is not None:
                    name = last.text
                    if initials is not None:
                        name += f" {initials.text}"
                    authors_list.append(name)
            data["authors"] = authors_list[:5] # Keep as list
            
            data["source"] = "pubmed"
            
            articles.append(data)
    except Exception as e:
        print(f"XML Parse Error: {e}")
    
    return articles

def run_ingestion():
    print(f"🚀 Starting FULL OpenSearch Ingestion to {ES_HOST}...")
    client = get_opensearch_client()
    
    # Check connection
    if not client.ping():
        print("❌ Could not connect to OpenSearch. check credentials.")
        return

    print("✅ Connected to OpenSearch!")

    index_name = "pubmed_articles"
    
    # Create index if not exists
    if not client.indices.exists(index=index_name):
        print(f"Creating index '{index_name}'...")
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "title": {"type": "text"},
                    "abstract": {"type": "text"},
                    "authors": {"type": "text"},
                    "publication_year": {"type": "keyword"},
                    "source": {"type": "keyword"},
                    "metadata": {"type": "object"}
                }
            }
        }
        client.indices.create(index=index_name, body=mapping)

    queries = [
        "cancer immunotherapy",
        "type 2 diabetes treatment",
        "alzheimers disease",
        "cardiovascular disease prevention",
        "CRISPR gene editing",
        "mRNA vaccine technology",
        "artificial intelligence in medicine",
        "gut microbiome health"
    ]

    total_indexed = 0
    
    for q in queries:
        print(f"\nProcessing: '{q}'")
        pmids = fetch_pubmed_ids(q, max_results=50)
        print(f"  Found {len(pmids)} IDs")
        
        articles = fetch_pubmed_details(pmids)
        print(f"  Parsed {len(articles)} articles")
        
        actions = []
        for doc in articles:
            doc["metadata"] = {
                "authors": doc["authors"],
                "publication_date": doc["publication_year"],
                "source": "pubmed"
            }
            actions.append({
                "_index": index_name,
                "_id": doc["id"],
                "_source": doc
            })
        
        if actions:
            success, failed = helpers.bulk(client, actions)
            total_indexed += success
            print(f"  Successfully indexed {success} documents.")
        
        time.sleep(1)

    print(f"\n\n🎉 Done! Total indexed: {total_indexed}")

if __name__ == "__main__":
    run_ingestion()
