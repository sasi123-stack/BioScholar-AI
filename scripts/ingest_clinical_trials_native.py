
import requests
import json
import time

# --- CONFIGURATION (Same as ingest_full_dataset_native.py) ---
ES_HOST = "assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net"
ES_USER = "0204784e62"
ES_PASS = "38aa998d6c5c2891232c"
ES_BASE_URL = f"https://{ES_HOST}:443"

CT_API_BASE = "https://clinicaltrials.gov/api/v2/studies"

def make_es_request(method, path, data=None):
    url = f"{ES_BASE_URL}/{path}"
    headers = {"Content-Type": "application/json"}
    auth = (ES_USER, ES_PASS)
    
    try:
        if method == "PUT":
            return requests.put(url, auth=auth, headers=headers, json=data)
        elif method == "POST":
            return requests.post(url, auth=auth, headers=headers, json=data)
        elif method == "DELETE":
            return requests.delete(url, auth=auth, headers=headers)
        elif method == "HEAD":
            return requests.head(url, auth=auth, headers=headers)
        elif method == "GET":
             return requests.get(url, auth=auth, headers=headers)
    except Exception as e:
        print(f"ES Request Error: {e}")
    return None

def fetch_clinical_trials(query, max_results=20):
    """Fetch clinical trials from ClinicalTrials.gov API v2."""
    params = {
        "query.term": query,
        "pageSize": max_results,
        "format": "json"
    }
    
    try:
        resp = requests.get(CT_API_BASE, params=params)
        if resp.status_code != 200:
            print(f"API Error {resp.status_code}: {resp.text}")
            return []
            
        data = resp.json()
        studies = data.get("studies", [])
        return parse_studies(studies)
    except Exception as e:
        print(f"ClinicalTrials Fetch Error: {e}")
        return []

def parse_studies(studies):
    """Parse ClinicalTrials.gov JSON into our schema."""
    parsed_studies = []
    
    for study in studies:
        try:
            protocol = study.get("protocolSection", {})
            id_module = protocol.get("identificationModule", {})
            title_module = protocol.get("descriptionModule", {})
            status_module = protocol.get("statusModule", {})
            design_module = protocol.get("designModule", {})
            
            # Extract basic info
            nct_id = id_module.get("nctId")
            if not nct_id: continue
            
            title = id_module.get("briefTitle") or id_module.get("officialTitle") or "No Title"
            summary = title_module.get("briefSummary", "")
            
            # Status & Phases
            status = status_module.get("overallStatus", "Unknown")
            phases = design_module.get("phases", [])
            phase_str = ", ".join(phases) if phases else "Not Applicable"
            
            # Conditions
            conditions_module = protocol.get("conditionsModule", {})
            conditions = conditions_module.get("conditions", [])
            
            # Dates
            start_date_struct = status_module.get("startDateStruct", {})
            start_date = start_date_struct.get("date", "")
            
            data = {
                "id": nct_id,
                "title": title,
                "abstract": summary, # Mapping summary to abstract for unified search
                "source": "clinical_trials",
                "url": f"https://clinicaltrials.gov/study/{nct_id}",
                "publication_date": start_date, # using start date as publication date proxy
                "metadata": {
                    "nct_id": nct_id,
                    "status": status,
                    "phases": phases,
                    "conditions": conditions,
                    "study_type": design_module.get("studyType", "Interventional"),
                    "locations": [] # keeping simple for now
                }
            }
            
            parsed_studies.append(data)
        except Exception as e:
            print(f"Study Parse Error: {e}")
            continue
            
    return parsed_studies

def run_ingestion():
    print("🚀 Starting Clinical Trials Ingestion...")
    
    # 1. Setup Index
    index_name = "clinical_trials"
    
    # Check if index exists
    resp = make_es_request("HEAD", index_name)
    if resp.status_code != 200:
        print(f"Creating index '{index_name}'...")
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "title": {"type": "text"},
                    "abstract": {"type": "text"},
                    "source": {"type": "keyword"},
                    "url": {"type": "keyword"},
                    "publication_date": {"type": "date", "format": "yyyy-MM-dd||yyyy-MM||yyyy"},
                    "metadata": {"type": "object"}
                }
            }
        }
        make_es_request("PUT", index_name, mapping)
        
    # 2. Define Queries (Expanded)
    queries = [
        # Major Diseases
        "cancer immunotherapy",
        "type 2 diabetes treatment",
        "alzheimers disease",
        "cardiovascular disease prevention",
        "parkinsons disease",
        "obesity metabolic syndrome",
        "chronic kidney disease management",
        "asthma biologics",
        "rheumatoid arthritis biologics",
        
        # Innovative Technologies
        "CRISPR gene editing",
        "mRNA vaccine",
        "CAR-T cell therapy",
        "nanomedicine",
        
        # Public Health & Mental Health
        "covid-19 long term effects",
        "depression cognitive behavioral therapy",
        "anxiety disorders treatment",
        "schizophrenia novel antipsychotics",
        "pediatric rare diseases"
    ]

    total_indexed = 0
    
    for q in queries:
        print(f"\nProcessing: '{q}'")
        
        # A. Fetch
        studies = fetch_clinical_trials(q, max_results=100) # API v2 default page size is often small, requesting 50
        print(f"  Found {len(studies)} studies")
        
        # B. Index
        count = 0
        for doc in studies:
            # Add metadata wrapper if needed by backend (the parser already adds it)
            
            # Index
            resp = make_es_request("PUT", f"{index_name}/_doc/{doc['id']}", doc)
            if resp and resp.status_code in [200, 201]:
                count += 1
                print(".", end="", flush=True)
            else:
                print("x", end="", flush=True)
                
        total_indexed += count
        print(f" -> {count} indexed")
        time.sleep(1) 

    print(f"\n\n🎉 Done! Total indexed: {total_indexed}")

if __name__ == "__main__":
    run_ingestion()
