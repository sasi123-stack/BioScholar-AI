"""Monitor the progress of data ingestion."""
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.indexing import ElasticsearchClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


def monitor_index_growth(interval_seconds=30, duration_minutes=60):
    """Monitor index growth over time.
    
    Args:
        interval_seconds: How often to check (in seconds)
        duration_minutes: How long to monitor (in minutes)
    """
    es_client = ElasticsearchClient()
    
    print("\n" + "="*80)
    print("📊 MONITORING INDEX GROWTH")
    print("="*80)
    print(f"Checking every {interval_seconds} seconds for {duration_minutes} minutes")
    print("Press Ctrl+C to stop monitoring\n")
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    previous_counts = {'pubmed_articles': 0, 'clinical_trials': 0}
    
    try:
        while time.time() < end_time:
            try:
                # Get current counts
                pubmed_count = es_client.count_documents('pubmed_articles')
                trials_count = es_client.count_documents('clinical_trials')
                total_count = pubmed_count + trials_count
                
                # Calculate growth
                pubmed_growth = pubmed_count - previous_counts['pubmed_articles']
                trials_growth = trials_count - previous_counts['clinical_trials']
                
                # Display status
                elapsed = (time.time() - start_time) / 60
                print(f"\n[{elapsed:.1f} min] Index Status:")
                print(f"  📚 PubMed Articles: {pubmed_count:,} (+{pubmed_growth})")
                print(f"  🧪 Clinical Trials: {trials_count:,} (+{trials_growth})")
                print(f"  📊 Total Documents: {total_count:,}")
                
                # Update previous counts
                previous_counts['pubmed_articles'] = pubmed_count
                previous_counts['clinical_trials'] = trials_count
                
                # Wait for next check
                time.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error checking index: {e}")
                time.sleep(interval_seconds)
                
    except KeyboardInterrupt:
        print("\n\n⚠️  Monitoring stopped by user")
    
    # Final summary
    print("\n" + "="*80)
    print("📊 FINAL STATUS")
    print("="*80)
    try:
        pubmed_count = es_client.count_documents('pubmed_articles')
        trials_count = es_client.count_documents('clinical_trials')
        total_count = pubmed_count + trials_count
        
        print(f"📚 PubMed Articles: {pubmed_count:,}")
        print(f"🧪 Clinical Trials: {trials_count:,}")
        print(f"📊 Total Documents: {total_count:,}")
        print("="*80)
    except Exception as e:
        logger.error(f"Error getting final counts: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor index growth.')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds')
    parser.add_argument('--duration', type=int, default=60, help='Monitoring duration in minutes')
    args = parser.parse_args()
    
    monitor_index_growth(
        interval_seconds=args.interval,
        duration_minutes=args.duration
    )
