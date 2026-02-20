"""Example usage of the data acquisition pipeline."""

from src.data_pipeline import PubMedFetcher, ClinicalTrialsFetcher, DataStorage

# Initialize components
pubmed = PubMedFetcher()
trials = ClinicalTrialsFetcher()
storage = DataStorage()

# Example 1: Fetch PubMed articles
print("Fetching PubMed articles...")
articles = pubmed.search_and_fetch(
    query="breast cancer immunotherapy",
    max_results=50,
    date_from="2023/01/01",
    date_to="2024/12/31"
)
print(f"Found {len(articles)} articles")

# Save articles
storage.save_pubmed_articles(articles, "breast cancer immunotherapy")

# Example 2: Fetch Clinical Trials
print("\nFetching clinical trials...")
trials_data = trials.search_and_fetch(
    condition="Alzheimer's Disease",
    intervention="Drug",
    max_results=30
)
print(f"Found {len(trials_data)} trials")

# Save trials
storage.save_clinical_trials(trials_data, "Alzheimer's Disease")

# Example 3: Load saved data
print("\nListing saved files...")
pubmed_files = storage.list_pubmed_files()
print(f"PubMed files: {pubmed_files}")

trial_files = storage.list_clinical_trials_files()
print(f"Clinical trials files: {trial_files}")
