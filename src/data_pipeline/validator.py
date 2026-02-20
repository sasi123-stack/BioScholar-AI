"""Data validation utilities."""

from typing import Dict, List, Tuple

from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataValidator:
    """Validates biomedical data quality."""
    
    @staticmethod
    def validate_pubmed_article(article: Dict) -> Tuple[bool, List[str]]:
        """Validate a PubMed article.
        
        Args:
            article: Article dictionary to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        if not article.get("id"):
            errors.append("Missing PMID")
        
        if not article.get("title"):
            errors.append("Missing title")
        
        if not article.get("abstract"):
            errors.append("Missing abstract")
        
        # Check field types
        if not isinstance(article.get("authors", []), list):
            errors.append("Authors must be a list")
        
        if not isinstance(article.get("mesh_terms", []), list):
            errors.append("MeSH terms must be a list")
        
        # Check text length
        title = article.get("title", "")
        if len(title) < 10:
            errors.append("Title too short (< 10 characters)")
        
        abstract = article.get("abstract", "")
        if len(abstract) < 50:
            errors.append("Abstract too short (< 50 characters)")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    @staticmethod
    def validate_clinical_trial(trial: Dict) -> Tuple[bool, List[str]]:
        """Validate a clinical trial.
        
        Args:
            trial: Trial dictionary to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        if not trial.get("id"):
            errors.append("Missing NCT ID")
        
        if not trial.get("title"):
            errors.append("Missing title")
        
        if not trial.get("abstract"):
            errors.append("Missing summary")
        
        # Check field types
        if not isinstance(trial.get("conditions", []), list):
            errors.append("Conditions must be a list")
        
        if not isinstance(trial.get("interventions", []), list):
            errors.append("Interventions must be a list")
        
        if not isinstance(trial.get("phases", []), list):
            errors.append("Phases must be a list")
        
        # Check text length
        title = trial.get("title", "")
        if len(title) < 10:
            errors.append("Title too short (< 10 characters)")
        
        summary = trial.get("abstract", "")
        if len(summary) < 50:
            errors.append("Summary too short (< 50 characters)")
        
        # Check enrollment
        enrollment = trial.get("enrollment", 0)
        if not isinstance(enrollment, (int, float)):
            errors.append("Enrollment must be a number")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    @staticmethod
    def validate_batch(
        documents: List[Dict],
        doc_type: str = "article"
    ) -> Tuple[List[Dict], List[Dict]]:
        """Validate a batch of documents.
        
        Args:
            documents: List of documents to validate
            doc_type: Type of document ('article' or 'trial')
            
        Returns:
            Tuple of (valid_documents, invalid_documents_with_errors)
        """
        valid = []
        invalid = []
        
        validator_func = (
            DataValidator.validate_pubmed_article
            if doc_type == "article"
            else DataValidator.validate_clinical_trial
        )
        
        for doc in documents:
            is_valid, errors = validator_func(doc)
            
            if is_valid:
                valid.append(doc)
            else:
                invalid.append({
                    "document": doc,
                    "errors": errors
                })
        
        logger.info(
            f"Validation: {len(valid)} valid, {len(invalid)} invalid "
            f"({doc_type}s)"
        )
        
        if invalid:
            logger.warning(f"Found {len(invalid)} invalid documents")
            for item in invalid[:5]:  # Log first 5
                logger.warning(
                    f"  ID: {item['document'].get('id', 'unknown')}, "
                    f"Errors: {', '.join(item['errors'])}"
                )
        
        return valid, invalid
