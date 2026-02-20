"""Data normalization for PubMed articles and clinical trials."""

from typing import Dict, List, Optional

from .text_cleaner import TextCleaner
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataNormalizer:
    """Normalizes and standardizes biomedical data."""
    
    def __init__(self):
        """Initialize data normalizer."""
        self.text_cleaner = TextCleaner()
    
    def normalize_pubmed_article(self, article: Dict) -> Dict:
        """Normalize a PubMed article.
        
        Args:
            article: Raw article dictionary
            
        Returns:
            Normalized article dictionary
        """
        try:
            # Clean text fields
            title = self.text_cleaner.clean(article.get("title", ""))
            abstract = self.text_cleaner.clean(article.get("abstract", ""))
            
            # Combine title and abstract for full text
            full_text = f"{title}. {abstract}".strip()
            
            # Clean journal name
            journal = self.text_cleaner.clean(
                article.get("journal", ""),
                remove_special=False
            )
            
            # Clean author names
            authors = [
                self.text_cleaner.clean(author, remove_special=False)
                for author in article.get("authors", [])
            ]
            
            # Clean MeSH terms
            mesh_terms = [
                self.text_cleaner.clean(term, remove_special=False)
                for term in article.get("mesh_terms", [])
            ]
            
            # Build normalized article
            normalized = {
                "id": article.get("pmid", ""),
                "source": "pubmed",
                "type": "article",
                "title": title,
                "abstract": abstract,
                "full_text": full_text,
                "authors": authors,
                "journal": journal,
                "publication_year": article.get("publication_year", ""),
                "publication_month": article.get("publication_month", ""),
                "publication_date": self._build_publication_date(
                    article.get("publication_year", ""),
                    article.get("publication_month", "")
                ),
                "mesh_terms": mesh_terms,
                "keywords": mesh_terms,  # Use MeSH terms as keywords
                "doi": article.get("doi", ""),
                "metadata": {
                    "source": "pubmed",
                    "pmid": article.get("pmid", ""),
                    "author_count": len(authors),
                    "has_abstract": bool(abstract),
                    "mesh_term_count": len(mesh_terms)
                }
            }
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing PubMed article: {e}")
            return {}
    
    def normalize_clinical_trial(self, trial: Dict) -> Dict:
        """Normalize a clinical trial.
        
        Args:
            trial: Raw trial dictionary
            
        Returns:
            Normalized trial dictionary
        """
        try:
            # Clean text fields
            title = self.text_cleaner.clean(trial.get("title", ""))
            summary = self.text_cleaner.clean(trial.get("summary", ""))
            
            # Combine title and summary for full text
            full_text = f"{title}. {summary}".strip()
            
            # Clean conditions
            conditions = [
                self.text_cleaner.clean(cond, remove_special=False)
                for cond in trial.get("conditions", [])
            ]
            
            # Clean interventions
            interventions = []
            for intervention in trial.get("interventions", []):
                if isinstance(intervention, dict):
                    interventions.append({
                        "type": self.text_cleaner.clean(
                            intervention.get("type", ""),
                            remove_special=False
                        ),
                        "name": self.text_cleaner.clean(
                            intervention.get("name", ""),
                            remove_special=False
                        ),
                        "description": self.text_cleaner.clean(
                            intervention.get("description", "")
                        )
                    })
                else:
                    interventions.append({
                        "type": "Unknown",
                        "name": self.text_cleaner.clean(str(intervention)),
                        "description": ""
                    })
            
            # Extract intervention names for keywords
            intervention_names = [i["name"] for i in interventions if i["name"]]
            
            # Clean outcomes
            primary_outcomes = [
                self.text_cleaner.clean(str(outcome), remove_special=False)
                for outcome in trial.get("primary_outcomes", [])
            ]
            
            secondary_outcomes = [
                self.text_cleaner.clean(str(outcome), remove_special=False)
                for outcome in trial.get("secondary_outcomes", [])
            ]
            
            # Clean locations
            locations = [
                self.text_cleaner.clean(loc, remove_special=False)
                for loc in trial.get("locations", [])
            ]
            
            # Extract year from start_date
            publication_date = trial.get("start_date", "")
            publication_year = ""
            if publication_date:
                # Try to extract YYYY from various formats
                import re
                year_match = re.search(r'\d{4}', publication_date)
                if year_match:
                    publication_year = year_match.group(0)
            
            normalized = {
                "id": trial.get("nct_id", ""),
                "source": "clinicaltrials",
                "type": "clinical_trial",
                "title": title,
                "abstract": summary,
                "full_text": full_text,
                "conditions": conditions,
                "interventions": interventions,
                "primary_outcomes": primary_outcomes,
                "secondary_outcomes": secondary_outcomes,
                "phases": trial.get("phases", []),
                "status": trial.get("status", ""),
                "enrollment": trial.get("enrollment", 0),
                "start_date": trial.get("start_date", ""),
                "completion_date": trial.get("completion_date", ""),
                "publication_date": publication_date,
                "publication_year": publication_year,
                "sponsor": self.text_cleaner.clean(
                    trial.get("sponsor", ""),
                    remove_special=False
                ),
                "locations": locations,
                "keywords": conditions + intervention_names,  # Combine for keywords
                "metadata": {
                    "source": "clinicaltrials",
                    "nct_id": trial.get("nct_id", ""),
                    "intervention_count": len(interventions),
                    "condition_count": len(conditions),
                    "location_count": len(locations),
                    "has_summary": bool(summary)
                }
            }
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing clinical trial: {e}")
            return {}
    
    def normalize_batch_pubmed(self, articles: List[Dict]) -> List[Dict]:
        """Normalize a batch of PubMed articles.
        
        Args:
            articles: List of raw article dictionaries
            
        Returns:
            List of normalized article dictionaries
        """
        normalized = []
        
        for article in articles:
            norm_article = self.normalize_pubmed_article(article)
            if norm_article:
                normalized.append(norm_article)
        
        logger.info(f"Normalized {len(normalized)}/{len(articles)} PubMed articles")
        return normalized
    
    def normalize_batch_trials(self, trials: List[Dict]) -> List[Dict]:
        """Normalize a batch of clinical trials.
        
        Args:
            trials: List of raw trial dictionaries
            
        Returns:
            List of normalized trial dictionaries
        """
        normalized = []
        
        for trial in trials:
            norm_trial = self.normalize_clinical_trial(trial)
            if norm_trial:
                normalized.append(norm_trial)
        
        logger.info(f"Normalized {len(normalized)}/{len(trials)} clinical trials")
        return normalized
    
    def _build_publication_date(self, year: str, month: str) -> str:
        """Build a publication date string.
        
        Args:
            year: Publication year
            month: Publication month
            
        Returns:
            Date string in YYYY-MM format or YYYY
        """
        if not year:
            return ""
        
        if month:
            # Convert month name to number
            month_map = {
                "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
                "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
                "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
            }
            month_num = month_map.get(month[:3], "01")
            return f"{year}-{month_num}"
        
        return year
