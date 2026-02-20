
import requests
import json
import time

# --- CONFIGURATION (Bonsai Opensearch) ---
ES_HOST = "assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net"
ES_USER = "0204784e62"
ES_PASS = "38aa998d6c5c2891232c"
ES_BASE_URL = f"https://{ES_HOST}:443"

CT_API_BASE = "https://clinicaltrials.gov/api/v2/studies"
TARGET_COUNT = 17106

def get_current_count():
    url = f"{ES_BASE_URL}/clinical_trials/_count"
    auth = (ES_USER, ES_PASS)
    try:
        resp = requests.get(url, auth=auth, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("count", 0)
    except Exception:
        pass
    return 0

def bulk_index(docs):
    if not docs:
        return 0
    
    url = f"{ES_BASE_URL}/_bulk"
    auth = (ES_USER, ES_PASS)
    headers = {"Content-Type": "application/x-ndjson"}
    
    bulk_data = ""
    for doc in docs:
        action = {"index": {"_index": "clinical_trials", "_id": doc["id"]}}
        bulk_data += json.dumps(action) + "\n"
        bulk_data += json.dumps(doc) + "\n"
    
    try:
        resp = requests.post(url, auth=auth, headers=headers, data=bulk_data, timeout=30)
        if resp.status_code == 200:
            res_json = resp.json()
            # Count only 'created' items if we want strict new count, 
            # but for reaching target, we just index.
            # Bonsai might return errors if we go too fast.
            return len(docs)
    except Exception as e:
        print(f"Bulk Error: {e}")
    return 0

def fetch_clinical_trials(query, pageSize=100, pageToken=None):
    params = {"query.term": query, "pageSize": pageSize, "format": "json"}
    if pageToken: params["pageToken"] = pageToken
    
    try:
        resp = requests.get(CT_API_BASE, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            studies = data.get("studies", [])
            next_token = data.get("nextPageToken")
            return parse_studies(studies), next_token
    except Exception:
        pass
    return [], None

def parse_studies(studies):
    parsed_studies = []
    for study in studies:
        try:
            protocol = study.get("protocolSection", {})
            id_module = protocol.get("identificationModule", {})
            title_module = protocol.get("descriptionModule", {})
            status_module = protocol.get("statusModule", {})
            design_module = protocol.get("designModule", {})
            nct_id = id_module.get("nctId")
            if not nct_id: continue
            
            data = {
                "id": nct_id,
                "title": id_module.get("briefTitle") or id_module.get("officialTitle") or "No Title",
                "abstract": title_module.get("briefSummary", ""),
                "source": "clinical_trials",
                "url": f"https://clinicaltrials.gov/study/{nct_id}",
                "publication_date": status_module.get("startDateStruct", {}).get("date", ""),
                "metadata": {
                    "nct_id": nct_id,
                    "status": status_module.get("overallStatus", "Unknown"),
                    "phases": design_module.get("phases", []),
                    "conditions": protocol.get("conditionsModule", {}).get("conditions", []),
                    "study_type": design_module.get("studyType", "Interventional")
                }
            }
            parsed_studies.append(data)
        except Exception: continue
    return parsed_studies

def run_ingestion():
    current_count = get_current_count()
    print(f"Starting BULK ingestion to reach target: {TARGET_COUNT}")
    print(f"Current count: {current_count}")
    
    search_terms = [
        "Cardiology", "Neurology", "Gastroenterology", "Pediatrics", "Geriatrics",
        "Mental Health", "Ophthalmology", "Dermatology", "Rare Disease", "Stem Cell",
        "Gene Therapy", "CRISPR", "Clinical Data", "Placebo", "Informed Consent",
        "Double Blind", "Randomized", "Phase 1", "Phase 2", "Phase 3",
        "Infection", "Autoimmune", "Cancer", "Diabetes", "Heart", "Lung", "Brain",
        "Liver", "Kidney", "Blood", "Skin", "Eye", "Bone", "Muscle", "Nerve",
        "Virus", "Bacteria", "Fungus", "Parasite", "Antibiotic", "Vaccine"
    ]

    for term in search_terms:
        if current_count >= TARGET_COUNT: break
        print(f"\nTerm: {term}")
        token = None
        for _ in range(10): # Up to 1000 results per term
            studies, token = fetch_clinical_trials(term, pageSize=100, pageToken=token)
            if not studies: break
            
            bulk_index(studies)
            # Re-fetch count every batch to be accurate (some might be duplicates)
            current_count = get_current_count()
            print(f"  Processed page. Current index count: {current_count}")
            
            if current_count >= TARGET_COUNT: break
            if not token: break
            time.sleep(1)

    print(f"Final count: {current_count}")

if __name__ == "__main__":
    run_ingestion()
