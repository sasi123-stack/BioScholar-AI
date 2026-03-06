
import sys
from pathlib import Path
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_pipeline import ClinicalTrialsFetcher, DataProcessor
from src.indexing import ElasticsearchClient, DocumentIndexer
from src.nlp_engine import EmbeddingGenerator
from src.utils.logger import get_logger

logger = get_logger(__name__)

def run_trials_ingestion(conditions, max_per_condition=10):
    """Run indexing for clinical trials with embeddings."""
    logger.info("🚀 Starting Clinical Trials Ingestion with Embeddings")
    
    fetcher = ClinicalTrialsFetcher()
    processor = DataProcessor()
    es_client = ElasticsearchClient()
    indexer = DocumentIndexer(es_client)
    # Using biobert as it's already in the cache
    embedding_generator = EmbeddingGenerator(model_type="biobert")
    
    all_trials = []
    seen_ids = set()
    
    for condition in conditions:
        logger.info(f"🧪 Fetching: '{condition}'")
        try:
            trials = fetcher.search_and_fetch(condition=condition, max_results=max_per_condition)
            for t in trials:
                if t['nct_id'] not in seen_ids:
                    seen_ids.add(t['nct_id'])
                    all_trials.append(t)
            logger.info(f"  ✅ Fetched {len(trials)} trials")
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"  ❌ Error: {e}")
            
    if not all_trials:
        logger.warning("No trials fetched.")
        return

    logger.info(f"📊 Processing and Indexing {len(all_trials)} unique trials...")
    processed, _ = processor.process_clinical_trials(all_trials)
    
    indexed_count = 0
    for i, trial in enumerate(processed, 1):
        try:
            # Normalizer moves 'summary' to 'abstract'
            if trial.get('abstract'):
                embedding = embedding_generator.generate_document_embedding(trial, fields=['title', 'abstract'])
                trial['embedding'] = embedding.tolist()
            
            indexer.index_document(
                index_name='clinical_trials',
                doc_id=trial['id'],
                document=trial
            )
            indexed_count += 1
            if indexed_count % 5 == 0:
                print(f"Indexed {indexed_count}/{len(processed)}...")
        except Exception as e:
            logger.error(f"Error indexing {trial.get('nct_id')}: {e}")
            
    logger.info(f"✨ Successfully indexed {indexed_count} clinical trials with embeddings.")

if __name__ == "__main__":
    expanded_queries = [
        "Huntington's disease", "Amyotrophic lateral sclerosis ALS", "Duchenne muscular dystrophy",
        "Spinal muscular atrophy", "Cystic fibrosis novel modulators", "Sickle cell disease gene therapy",
        "Thalassemia gene editing", "Hypertrophic cardiomyopathy", "TAVR heart valve", "MitraClip outcomes",
        "Left ventricular assist device", "Bioabsorbable stents", "Renal denervation hypertension",
        "Glioblastoma immunotherapy", "Ovarian cancer PARP inhibitors", "Multiple myeloma BCMA",
        "Hepatocellular carcinoma systemic", "Sarcoma targeted therapy", "Liquid biopsy clinical utility",
        "Radiopharmaceuticals theranostics", "Systemic lupus erythematosus biologics", "Psoriatic arthritis novel IL-23",
        "Ankylosing spondylitis JAK inhibitors", "Sjogren's syndrome treatment", "Vasculitis immunosuppression",
        "Progressive supranuclear palsy", "Chronic traumatic encephalopathy", "Ketamine for treatment-resistant depression",
        "Psilocybin therapy for PTSD", "Transcranial magnetic stimulation OCD", "Deep brain stimulation for movement disorders",
        "Antimicrobial resistance novel antibiotics", "Clostridioides difficile fecal transplant", "Lyme disease chronic effects",
        "Epstein-Barr virus vaccine", "Dengue fever vaccine trial", "Zika virus therapeutic", "Nonalcoholic steatohepatitis NASH",
        "Cushing's syndrome medical therapy", "Acromegaly somatostatin analogs", "Polycystic ovary syndrome metformin",
        "Continuous glucose monitoring type 1", "Wet age-related macular degeneration", "Glaucoma minimally invasive surgery",
        "Diabetic retinopathy anti-VEGF", "Gene therapy for retinal dystrophy", "N-of-1 clinical trials",
        "Adaptive clinical trial design", "Virtual clinical trials decentralized", "Real-world evidence oncology",
        "AI in clinical trial recruitment"
    ]
    # Limiting for broad coverage
    run_trials_ingestion(expanded_queries, max_per_condition=10)
