"""PubMed data fetcher using NCBI E-utilities API."""

import time
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from src.utils.config import settings, yaml_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PubMedFetcher:
    """Fetches articles from PubMed using Entrez E-utilities API."""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        email: Optional[str] = None,
        rate_limit: int = 10
    ):
        """Initialize PubMed fetcher.
        
        Args:
            api_key: NCBI API key (optional, increases rate limit)
            email: Email address (required by NCBI)
            rate_limit: Requests per second (10 with key, 3 without)
        """
        self.api_key = api_key or settings.pubmed_api_key
        # Check for placeholder default value and ignore it
        if self.api_key and "your_ncbi_api_key_here" in self.api_key:
            logger.warning("Ignoring placeholder PubMed API Key found in settings.")
            self.api_key = None
            
        self.email = email or settings.pubmed_email
        if self.email and "your_email@example.com" in self.email:
             # If using default email from .env, replace or warn
             # Often NCBI blocks requests without email or with invalid ones?
             # But 'student@university.edu' is passed in the caller, so it should be fine there.
             # However, this logic here loads from settings if email arg is None.
             pass

        self.rate_limit = rate_limit
        self.last_request_time = 0
        
        if not self.email:
            logger.warning("No email provided for PubMed API. This is required by NCBI.")
        
        logger.info(f"PubMed fetcher initialized (rate_limit={rate_limit} req/s)")
    
    def _rate_limit_wait(self):
        """Enforce rate limiting between requests."""
        if self.rate_limit > 0:
            min_interval = 1.0 / self.rate_limit
            elapsed = time.time() - self.last_request_time
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()
    
    def _build_params(self, **kwargs) -> Dict:
        """Build common parameters for API requests."""
        params = {
            "email": self.email,
            **kwargs
        }
        if self.api_key:
            params["api_key"] = self.api_key
        return params
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _make_request(self, endpoint: str, params: Dict) -> requests.Response:
        """Make HTTP request with retry logic.
        
        Args:
            endpoint: API endpoint (e.g., 'esearch.fcgi')
            params: Query parameters
            
        Returns:
            Response object
        """
        self._rate_limit_wait()
        url = f"{self.BASE_URL}{endpoint}"
        
        logger.debug(f"Request: {endpoint} with params: {params}")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        return response
    
    def search(
        self,
        query: str,
        max_results: int = 100,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        retstart: int = 0
    ) -> List[str]:
        """Search PubMed for articles matching query.
        
        Args:
            query: Search query (e.g., "cancer treatment")
            max_results: Maximum number of results to return
            date_from: Start date (YYYY/MM/DD format)
            date_to: End date (YYYY/MM/DD format)
            retstart: Starting index for pagination
            
        Returns:
            List of PubMed IDs (PMIDs)
        """
        params = self._build_params(
            db="pubmed",
            term=query,
            retmax=max_results,
            retstart=retstart,
            retmode="json"
        )
        
        if date_from:
            params["mindate"] = date_from
        if date_to:
            params["maxdate"] = date_to
        
        try:
            response = self._make_request("esearch.fcgi", params)
            data = response.json()
            
            pmids = data.get("esearchresult", {}).get("idlist", [])
            count = int(data.get("esearchresult", {}).get("count", 0))
            
            logger.info(f"Found {count} articles for query: '{query}' (returning {len(pmids)})")
            return pmids
            
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            raise
    
    def fetch_details(
        self,
        pmids: List[str],
        batch_size: int = 200
    ) -> List[Dict]:
        """Fetch detailed article information for given PMIDs.
        
        Args:
            pmids: List of PubMed IDs
            batch_size: Number of articles to fetch per request
            
        Returns:
            List of article dictionaries with parsed data
        """
        if not pmids:
            return []
        
        all_articles = []
        
        # Process in batches
        for i in range(0, len(pmids), batch_size):
            batch_pmids = pmids[i:i + batch_size]
            
            params = self._build_params(
                db="pubmed",
                id=",".join(batch_pmids),
                retmode="xml"
            )
            
            try:
                response = self._make_request("efetch.fcgi", params)
                articles = self._parse_xml_response(response.text)
                all_articles.extend(articles)
                
                logger.info(f"Fetched {len(articles)} articles (batch {i//batch_size + 1})")
                
            except Exception as e:
                logger.error(f"Failed to fetch batch starting at {i}: {e}")
                continue
        
        return all_articles
    
    def _parse_xml_response(self, xml_text: str) -> List[Dict]:
        """Parse XML response from PubMed efetch.
        
        Args:
            xml_text: Raw XML response text
            
        Returns:
            List of parsed article dictionaries
        """
        articles = []
        
        try:
            root = ET.fromstring(xml_text)
            
            for article_elem in root.findall(".//PubmedArticle"):
                article_data = self._extract_article_data(article_elem)
                if article_data:
                    articles.append(article_data)
                    
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
        
        return articles
    
    def _extract_article_data(self, article_elem: ET.Element) -> Optional[Dict]:
        """Extract structured data from article XML element.
        
        Args:
            article_elem: XML element for a single article
            
        Returns:
            Dictionary with article data or None if parsing fails
        """
        try:
            medline_citation = article_elem.find(".//MedlineCitation")
            article = article_elem.find(".//Article")
            
            if medline_citation is None or article is None:
                return None
            
            # Extract PMID
            pmid_elem = medline_citation.find("PMID")
            pmid = pmid_elem.text if pmid_elem is not None else None
            
            # Extract title
            title_elem = article.find(".//ArticleTitle")
            title = title_elem.text if title_elem is not None else ""
            
            # Extract abstract
            abstract_texts = article.findall(".//AbstractText")
            abstract = " ".join([
                abs_elem.text for abs_elem in abstract_texts 
                if abs_elem.text is not None
            ])
            
            # Extract authors
            authors = []
            for author in article.findall(".//Author"):
                lastname = author.find("LastName")
                forename = author.find("ForeName")
                if lastname is not None and forename is not None:
                    authors.append(f"{forename.text} {lastname.text}")
            
            # Extract journal info
            journal = article.find(".//Journal")
            journal_title = ""
            if journal is not None:
                journal_title_elem = journal.find(".//Title")
                journal_title = journal_title_elem.text if journal_title_elem is not None else ""
            
            # Extract publication date
            pub_date_elem = article.find(".//PubDate")
            pub_year = ""
            pub_month = ""
            if pub_date_elem is not None:
                year_elem = pub_date_elem.find("Year")
                month_elem = pub_date_elem.find("Month")
                pub_year = year_elem.text if year_elem is not None else ""
                pub_month = month_elem.text if month_elem is not None else ""
            
            # Extract MeSH terms
            mesh_terms = []
            for mesh in medline_citation.findall(".//MeshHeading/DescriptorName"):
                if mesh.text:
                    mesh_terms.append(mesh.text)
            
            # Extract DOI
            doi = None
            for article_id in article_elem.findall(".//ArticleId"):
                if article_id.get("IdType") == "doi":
                    doi = article_id.text
                    break
            
            return {
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "journal": journal_title,
                "publication_year": pub_year,
                "publication_month": pub_month,
                "mesh_terms": mesh_terms,
                "doi": doi,
                "source": "pubmed"
            }
            
        except Exception as e:
            logger.error(f"Error extracting article data: {e}")
            return None
    
    def search_and_fetch(
        self,
        query: str,
        max_results: int = 100,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Dict]:
        """Combined search and fetch operation.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            date_from: Start date filter
            date_to: End date filter
            
        Returns:
            List of article dictionaries with full details
        """
        logger.info(f"Searching PubMed: '{query}' (max_results={max_results})")
        
        # Search for PMIDs
        pmids = self.search(
            query=query,
            max_results=max_results,
            date_from=date_from,
            date_to=date_to
        )
        
        if not pmids:
            logger.warning(f"No results found for query: '{query}'")
            return []
        
        # Fetch detailed article data
        articles = self.fetch_details(pmids)
        
        logger.info(f"Successfully fetched {len(articles)} articles")
        return articles
