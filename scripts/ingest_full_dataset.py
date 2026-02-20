"""Full dataset ingestion script - fetches and indexes large amounts of data."""

import sys
from pathlib import Path
from typing import List, Dict
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_pipeline import PubMedFetcher, ClinicalTrialsFetcher, DataProcessor
from src.indexing import ElasticsearchClient, DocumentIndexer
from src.nlp_engine import EmbeddingGenerator
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataIngestionPipeline:
    """Pipeline for fetching, processing, and indexing large datasets."""
    
    def __init__(self):
        """Initialize pipeline components."""
        self.pubmed_fetcher = PubMedFetcher()
        self.trials_fetcher = ClinicalTrialsFetcher()
        self.processor = DataProcessor()
        self.es_client = ElasticsearchClient()
        self.indexer = DocumentIndexer(self.es_client)
        self.embedding_generator = EmbeddingGenerator(model_type="biobert")
        
        logger.info("✅ Pipeline initialized")
    
    def fetch_pubmed_articles(
        self,
        queries: List[str],
        max_per_query: int = 100
    ) -> List[Dict]:
        """Fetch PubMed articles for multiple queries.
        
        Args:
            queries: List of search queries
            max_per_query: Maximum articles per query
            
        Returns:
            List of all fetched articles
        """
        all_articles = []
        seen_pmids = set()
        
        for query in queries:
            logger.info(f"📚 Fetching PubMed articles: '{query}'")
            try:
                articles = self.pubmed_fetcher.search_and_fetch(
                    query=query,
                    max_results=max_per_query
                )
                
                # Deduplicate by PMID
                unique_articles = []
                for article in articles:
                    pmid = article.get('pmid')
                    if pmid and pmid not in seen_pmids:
                        seen_pmids.add(pmid)
                        unique_articles.append(article)
                
                all_articles.extend(unique_articles)
                logger.info(f"  ✅ Fetched {len(unique_articles)} unique articles (Total: {len(all_articles)})")
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"  ❌ Error fetching '{query}': {e}")
                continue
        
        return all_articles
    
    def fetch_clinical_trials(
        self,
        conditions: List[str],
        max_per_condition: int = 100
    ) -> List[Dict]:
        """Fetch clinical trials for multiple conditions.
        
        Args:
            conditions: List of medical conditions
            max_per_condition: Maximum trials per condition
            
        Returns:
            List of all fetched trials
        """
        all_trials = []
        seen_nct_ids = set()
        
        for condition in conditions:
            logger.info(f"🧪 Fetching Clinical Trials: '{condition}'")
            try:
                trials = self.trials_fetcher.search_and_fetch(
                    condition=condition,
                    max_results=max_per_condition
                )
                
                # Deduplicate by NCT ID
                unique_trials = []
                for trial in trials:
                    nct_id = trial.get('nct_id')
                    if nct_id and nct_id not in seen_nct_ids:
                        seen_nct_ids.add(nct_id)
                        unique_trials.append(trial)
                
                all_trials.extend(unique_trials)
                logger.info(f"  ✅ Fetched {len(unique_trials)} unique trials (Total: {len(all_trials)})")
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"  ❌ Error fetching '{condition}': {e}")
                continue
        
        return all_trials
    
    def process_and_index_pubmed(self, articles: List[Dict]):
        """Process and index PubMed articles.
        
        Args:
            articles: List of PubMed articles
        """
        logger.info(f"\n📊 Processing {len(articles)} PubMed articles...")
        
        # Process articles (returns tuple: valid, invalid)
        processed, invalid = self.processor.process_pubmed_articles(articles)
        logger.info(f"  ✅ Processed {len(processed)} articles ({len(invalid)} invalid)")
        
        # Generate embeddings and index
        logger.info("  🧠 Generating embeddings and indexing...")
        indexed_count = 0
        failed_count = 0
        
        for i, article in enumerate(processed, 1):
            try:
                # Generate embedding for abstract
                if article.get('abstract'):
                    embedding = self.embedding_generator.generate_document_embedding(
                        article,
                        fields=['title', 'abstract']
                    )
                    article['embedding'] = embedding.tolist()
                
                # Index document
                doc_id = article.get('pmid', f"pubmed_{i}")
                self.indexer.index_document(
                    index_name='pubmed_articles',
                    doc_id=str(doc_id),
                    document=article
                )
                indexed_count += 1
                
                if indexed_count % 10 == 0:
                    logger.info(f"    Indexed {indexed_count}/{len(processed)} articles...")
                    
            except Exception as e:
                logger.error(f"    ❌ Error indexing article {i}: {e}")
                failed_count += 1
                continue
        
        logger.info(f"  ✅ Indexed {indexed_count} articles ({failed_count} failed)")
    
    def process_and_index_trials(self, trials: List[Dict]):
        """Process and index clinical trials.
        
        Args:
            trials: List of clinical trials
        """
        logger.info(f"\n🧪 Processing {len(trials)} clinical trials...")
        
        # Process trials (returns tuple: valid, invalid)
        processed, invalid = self.processor.process_clinical_trials(trials)
        logger.info(f"  ✅ Processed {len(processed)} trials ({len(invalid)} invalid)")
        
        # Generate embeddings and index
        logger.info("  🧠 Generating embeddings and indexing...")
        indexed_count = 0
        failed_count = 0
        
        for i, trial in enumerate(processed, 1):
            try:
                # Generate embedding for summary
                if trial.get('summary'):
                    embedding = self.embedding_generator.generate_document_embedding(
                        trial,
                        fields=['title', 'summary']
                    )
                    trial['embedding'] = embedding.tolist()
                
                # Index document
                doc_id = trial.get('nct_id', f"trial_{i}")
                self.indexer.index_document(
                    index_name='clinical_trials',
                    doc_id=str(doc_id),
                    document=trial
                )
                indexed_count += 1
                
                if indexed_count % 10 == 0:
                    logger.info(f"    Indexed {indexed_count}/{len(processed)} trials...")
                    
            except Exception as e:
                logger.error(f"    ❌ Error indexing trial {i}: {e}")
                failed_count += 1
                continue
        
        logger.info(f"  ✅ Indexed {indexed_count} trials ({failed_count} failed)")


def main():
    """Run full data ingestion pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ingest biomedical data.')
    parser.add_argument('--max-per-query', type=int, default=500, help='Max articles per query')
    parser.add_argument('--max-per-condition', type=int, default=500, help='Max trials per condition')
    args = parser.parse_args()

    logger.info("="*80)
    logger.info("🚀 FULL DATASET INGESTION PIPELINE")
    logger.info(f"Configuration: {args.max_per_query} articles/query, {args.max_per_condition} trials/condition")
    logger.info("="*80)
    
    # Define comprehensive search queries
    pubmed_queries = [
        "COVID-19 treatment",
        "SARS-CoV-2 vaccine",
        "cancer immunotherapy",
        "diabetes mellitus management",
        "Alzheimer disease therapy",
        "cardiovascular disease prevention",
        "hypertension treatment",
        "depression mental health",
        "obesity metabolic syndrome",
        "asthma chronic obstructive",
        "rheumatoid arthritis treatment",
        "HIV antiretroviral therapy",
        "tuberculosis drug resistance",
        "malaria prevention treatment",
        "hepatitis C antiviral",
        "stroke prevention management",
        "chronic kidney disease",
        "liver cirrhosis fibrosis",
        "multiple sclerosis therapy",
        "Parkinson disease treatment",
        "anxiety disorder treatment",
        "bipolar disorder management",
        "schizophrenia antipsychotic",
        "autism spectrum disorder",
        "ADHD management"
    ]
    
    clinical_trial_conditions = [
        "COVID-19",
        "Cancer",
        "Diabetes Mellitus",
        "Alzheimer Disease",
        "Cardiovascular Diseases",
        "Hypertension",
        "Depression",
        "Obesity",
        "Asthma",
        "Arthritis Rheumatoid",
        "HIV Infections",
        "Tuberculosis",
        "Malaria",
        "Hepatitis C",
        "Stroke",
        "Chronic Kidney Disease",
        "Liver Cirrhosis",
        "Multiple Sclerosis",
        "Parkinson Disease",
        "Breast Cancer",
        "Anxiety Disorders",
        "Bipolar Disorder",
        "Schizophrenia",
        "Autism Spectrum Disorder",
        "Attention Deficit Hyperactivity Disorder"
    ]
    
    start_time = time.time()
    
    try:
        pipeline = DataIngestionPipeline()
        
        # Fetch PubMed articles
        logger.info("\n" + "="*80)
        logger.info("📚 FETCHING PUBMED ARTICLES")
        logger.info("="*80)
        articles = pipeline.fetch_pubmed_articles(
            queries=pubmed_queries,
            max_per_query=args.max_per_query
        )
        logger.info(f"\n✅ Total unique PubMed articles fetched: {len(articles)}")
        
        # Fetch Clinical Trials
        logger.info("\n" + "="*80)
        logger.info("🧪 FETCHING CLINICAL TRIALS")
        logger.info("="*80)
        trials = pipeline.fetch_clinical_trials(
            conditions=clinical_trial_conditions,
            max_per_condition=args.max_per_condition
        )
        logger.info(f"\n✅ Total unique clinical trials fetched: {len(trials)}")
        
        # Process and index PubMed articles
        if articles:
            logger.info("\n" + "="*80)
            logger.info("📊 PROCESSING & INDEXING PUBMED ARTICLES")
            logger.info("="*80)
            pipeline.process_and_index_pubmed(articles)
        
        # Process and index Clinical Trials
        if trials:
            logger.info("\n" + "="*80)
            logger.info("🧪 PROCESSING & INDEXING CLINICAL TRIALS")
            logger.info("="*80)
            pipeline.process_and_index_trials(trials)
        
        # Summary
        elapsed_time = time.time() - start_time
        logger.info("\n" + "="*80)
        logger.info("✨ INGESTION COMPLETE")
        logger.info("="*80)
        logger.info(f"📚 PubMed Articles: {len(articles)}")
        logger.info(f"🧪 Clinical Trials: {len(trials)}")
        logger.info(f"⏱️  Total Time: {elapsed_time/60:.2f} minutes")
        logger.info("="*80)
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
