"""Script to generate and update embeddings for indexed documents."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.nlp_engine import ModelLoader, EmbeddingGenerator
from src.indexing import ElasticsearchClient, DocumentIndexer
from src.utils.logger import get_logger

logger = get_logger(__name__)


def generate_embeddings_for_pubmed():
    """Generate embeddings for PubMed articles and update index."""
    logger.info("=" * 60)
    logger.info("Generating Embeddings for PubMed Articles")
    logger.info("=" * 60)
    
    # Load processed documents
    processed_dir = Path("data/processed/pubmed")
    processed_files = list(processed_dir.glob("processed_pubmed_*.json"))
    
    if not processed_files:
        logger.warning("No processed PubMed files found")
        return
    
    latest_file = max(processed_files, key=lambda p: p.stat().st_mtime)
    logger.info(f"Loading documents from: {latest_file.name}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract articles from wrapper
    if isinstance(data, dict) and 'articles' in data:
        documents = data['articles']
    else:
        documents = data if isinstance(data, list) else []
    
    logger.info(f"Loaded {len(documents)} PubMed articles")
    
    # Initialize embedding generator (using BioBERT)
    logger.info("Initializing BioBERT model...")
    embedding_gen = EmbeddingGenerator(model_type="biobert", batch_size=4)
    
    # Generate embeddings
    logger.info("Generating embeddings...")
    embeddings = embedding_gen.generate_batch_embeddings(
        documents,
        fields=['title', 'abstract'],
        show_progress=True
    )
    
    # Create new documents with embeddings
    updated_documents = []
    for doc, embedding in zip(documents, embeddings):
        updated_doc = doc.copy()
        updated_doc['embedding'] = embedding.tolist()
        updated_documents.append(updated_doc)
    
    logger.info(f"✅ Generated embeddings for {len(updated_documents)} articles")
    
    # Update Elasticsearch index
    logger.info("Updating Elasticsearch index...")
    es_client = ElasticsearchClient()
    indexer = DocumentIndexer(es_client)
    
    success, failed = indexer.index_batch("pubmed_articles", updated_documents)
    logger.info(f"✅ Updated {success} documents in Elasticsearch")
    
    if failed > 0:
        logger.warning(f"⚠️  {failed} documents failed to update")
    
    # Cleanup
    es_client.close()


def generate_embeddings_for_trials():
    """Generate embeddings for clinical trials and update index."""
    logger.info("\n" + "=" * 60)
    logger.info("Generating Embeddings for Clinical Trials")
    logger.info("=" * 60)
    
    # Load processed documents
    processed_dir = Path("data/processed/clinical_trials")
    processed_files = list(processed_dir.glob("processed_trials_*.json"))
    
    if not processed_files:
        logger.warning("No processed trial files found")
        return
    
    latest_file = max(processed_files, key=lambda p: p.stat().st_mtime)
    logger.info(f"Loading documents from: {latest_file.name}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract trials from wrapper
    if isinstance(data, dict) and 'trials' in data:
        documents = data['trials']
    else:
        documents = data if isinstance(data, list) else []
    
    logger.info(f"Loaded {len(documents)} clinical trials")
    
    # Initialize embedding generator (using ClinicalBERT)
    logger.info("Initializing ClinicalBERT model...")
    embedding_gen = EmbeddingGenerator(model_type="clinicalbert", batch_size=4)
    
    # Generate embeddings
    logger.info("Generating embeddings...")
    embeddings = embedding_gen.generate_batch_embeddings(
        documents,
        fields=['title', 'summary'],
        show_progress=True
    )
    
    # Create new documents with embeddings
    updated_documents = []
    for doc, embedding in zip(documents, embeddings):
        updated_doc = doc.copy()
        updated_doc['embedding'] = embedding.tolist()
        updated_documents.append(updated_doc)
    
    logger.info(f"✅ Generated embeddings for {len(updated_documents)} trials")
    
    # Update Elasticsearch index
    logger.info("Updating Elasticsearch index...")
    es_client = ElasticsearchClient()
    indexer = DocumentIndexer(es_client)
    
    success, failed = indexer.index_batch("clinical_trials", updated_documents)
    logger.info(f"✅ Updated {success} documents in Elasticsearch")
    
    if failed > 0:
        logger.warning(f"⚠️  {failed} documents failed to update")
    
    # Cleanup
    es_client.close()


def test_similarity():
    """Test embedding similarity computation."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Embedding Similarity")
    logger.info("=" * 60)
    
    # Initialize generator
    embedding_gen = EmbeddingGenerator(model_type="biobert")
    
    # Test texts
    texts = [
        "COVID-19 treatment with antiviral drugs",
        "Coronavirus therapy using antivirals",
        "Diabetes management with insulin",
    ]
    
    logger.info("Generating embeddings for test texts...")
    embeddings = embedding_gen.encode_text(texts)
    
    # Compare similarities
    logger.info("\nSimilarity matrix:")
    for i, text1 in enumerate(texts):
        for j, text2 in enumerate(texts):
            if i < j:
                sim = embedding_gen.compute_similarity(embeddings[i], embeddings[j])
                logger.info(f"  Text {i+1} vs Text {j+1}: {sim:.4f}")
    
    logger.info("\nExpected: High similarity between texts 1-2, low between 1-3 and 2-3")


def main():
    """Main execution function."""
    try:
        # Generate embeddings for PubMed articles
        generate_embeddings_for_pubmed()
        
        # Generate embeddings for clinical trials
        generate_embeddings_for_trials()
        
        # Test similarity
        test_similarity()
        
        logger.info("\n" + "=" * 60)
        logger.info("✨ Embedding generation completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
