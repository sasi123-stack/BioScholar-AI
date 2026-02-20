
import requests
import json
import time

# --- CONFIGURATION (Bonsai Opensearch) ---
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
            return requests.put(url, auth=auth, headers=headers, json=data, timeout=10)
        elif method == "POST":
            return requests.post(url, auth=auth, headers=headers, json=data, timeout=10)
        elif method == "DELETE":
            return requests.delete(url, auth=auth, headers=headers, timeout=10)
        elif method == "HEAD":
            return requests.head(url, auth=auth, headers=headers, timeout=10)
        elif method == "GET":
             return requests.get(url, auth=auth, headers=headers, timeout=10)
    except Exception as e:
        print(f"\nES Request Error: {e}")
    return None

def fetch_clinical_trials(query, max_results=100):
    """Fetch clinical trials from ClinicalTrials.gov API v2."""
    params = {
        "query.term": query,
        "pageSize": max_results,
        "format": "json"
    }
    
    try:
        resp = requests.get(CT_API_BASE, params=params, timeout=15)
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
                    "locations": [] 
                }
            }
            
            parsed_studies.append(data)
        except Exception as e:
            print(f"Study Parse Error: {e}")
            continue
            
    return parsed_studies

def run_ingestion():
    print("Starting EXPANDED Clinical Trials Ingestion Pipeline...")
    
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
        
    # 2. Define Comprehensive Queries (Expanded)
    queries = [
        # Rare Diseases & Orphan Drugs
        "Huntington's disease",
        "Amyotrophic lateral sclerosis ALS",
        "Duchenne muscular dystrophy",
        "Spinal muscular atrophy",
        "Cystic fibrosis novel modulators",
        "Sickle cell disease gene therapy",
        "Thalassemia gene editing",
        
        # Innovative Cardiology
        "Hypertrophic cardiomyopathy",
        "TAVR heart valve",
        "MitraClip outcomes",
        "Left ventricular assist device",
        "Bioabsorbable stents",
        "Renal denervation hypertension",
        
        # Advanced Oncology
        "Glioblastoma immunotherapy",
        "Ovarian cancer PARP inhibitors",
        "Multiple myeloma BCMA",
        "Hepatocellular carcinoma systemic",
        "Sarcoma targeted therapy",
        "Liquid biopsy clinical utility",
        "Radiopharmaceuticals theranostics",
        
        # Immunology & Rheumatology
        "Systemic lupus erythematosus biologics",
        "Psoriatic arthritis novel IL-23",
        "Ankylosing spondylitis JAK inhibitors",
        "Sjogren's syndrome treatment",
        "Vasculitis immunosuppression",
        
        # Neurology & Psychiatry
        "Progressive supranuclear palsy",
        "Chronic traumatic encephalopathy",
        "Ketamine for treatment-resistant depression",
        "Psilocybin therapy for PTSD",
        "Transcranial magnetic stimulation OCD",
        "Deep brain stimulation for movement disorders",
        
        # Infectious Disease
        "Antimicrobial resistance novel antibiotics",
        "Clostridioides difficile fecal transplant",
        "Lyme disease chronic effects",
        "Epstein-Barr virus vaccine",
        "Dengue fever vaccine trial",
        "Zika virus therapeutic",
        
        # Endocrinology & Metabolism
        "Nonalcoholic steatohepatitis NASH",
        "Cushing's syndrome medical therapy",
        "Acromegaly somatostatin analogs",
        "Polycystic ovary syndrome metformin",
        "Continuous glucose monitoring type 1",
        
        # Ophthalmology
        "Wet age-related macular degeneration",
        "Glaucoma minimally invasive surgery",
        "Diabetic retinopathy anti-VEGF",
        "Gene therapy for retinal dystrophy",
        
        # Modern Methods
        "N-of-1 clinical trials",
        "Adaptive clinical trial design",
        "Virtual clinical trials decentralized",
        "Real-world evidence oncology",
        "AI in clinical trial recruitment"
    ]

    total_indexed = 0
    
    for q in queries:
        print(f"\nProcessing query: '{q}'")
        
        # A. Fetch (reduced per batch to see progress)
        studies = fetch_clinical_trials(q, max_results=50)
        print(f"  Fetched {len(studies)} studies from API")
        
        # B. Index
        count = 0
        for doc in studies:
            # Index
            resp = make_es_request("PUT", f"{index_name}/_doc/{doc['id']}", doc)
            if resp and resp.status_code in [200, 201]:
                count += 1
                print(".", end="", flush=True)
            else:
                code = resp.status_code if resp else "None"
                print(f"x({code})", end="", flush=True)
                
        total_indexed += count
        print(f"\n  Indexed {count} docs for this query")
        time.sleep(1) # Be nice to the API

    print(f"\n\nDone! Total indexed: {total_indexed}")

if __name__ == "__main__":
    run_ingestion()
