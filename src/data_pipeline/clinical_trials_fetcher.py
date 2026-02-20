"""ClinicalTrials.gov data fetcher."""

import time
from typing import Dict, List, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ClinicalTrialsFetcher:
    """Fetches clinical trial data from ClinicalTrials.gov API v2."""
    
    BASE_URL = "https://clinicaltrials.gov/api/v2"
    
    def __init__(self, rate_limit: int = 5):
        """Initialize ClinicalTrials fetcher.
        
        Args:
            rate_limit: Requests per second (default: 5)
        """
        self.rate_limit = rate_limit
        self.last_request_time = 0
        
        logger.info(f"ClinicalTrials fetcher initialized (rate_limit={rate_limit} req/s)")
    
    def _rate_limit_wait(self):
        """Enforce rate limiting between requests."""
        if self.rate_limit > 0:
            min_interval = 1.0 / self.rate_limit
            elapsed = time.time() - self.last_request_time
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _make_request(self, endpoint: str, params: Dict) -> requests.Response:
        """Make HTTP request with retry logic.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            Response object
        """
        self._rate_limit_wait()
        url = f"{self.BASE_URL}/{endpoint}"
        
        logger.debug(f"Request: {endpoint} with params: {params}")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        return response
    
    def search(
        self,
        query: Optional[str] = None,
        condition: Optional[str] = None,
        intervention: Optional[str] = None,
        status: Optional[List[str]] = None,
        page_size: int = 100,
        page_token: Optional[str] = None
    ) -> Dict:
        """Search for clinical trials.
        
        Args:
            query: General search query
            condition: Specific condition/disease
            intervention: Specific intervention/treatment
            status: List of recruitment statuses (e.g., ['RECRUITING', 'COMPLETED'])
            page_size: Number of results per page (max 1000)
            page_token: Token for pagination
            
        Returns:
            Dictionary with studies and next page token
        """
        params = {
            "format": "json",
            "pageSize": min(page_size, 1000)
        }
        
        # Build query filter
        filters = []
        if query:
            params["query.term"] = query
        if condition:
            params["query.cond"] = condition
        if intervention:
            params["query.intr"] = intervention
        if status:
            params["filter.overallStatus"] = ",".join(status)
        
        if page_token:
            params["pageToken"] = page_token
        
        try:
            response = self._make_request("studies", params)
            data = response.json()
            
            studies = data.get("studies", [])
            next_token = data.get("nextPageToken")
            total_count = data.get("totalCount", 0)
            
            logger.info(f"Found {total_count} trials (returning {len(studies)} in this page)")
            
            return {
                "studies": studies,
                "next_page_token": next_token,
                "total_count": total_count
            }
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def fetch_details(self, nct_ids: List[str]) -> List[Dict]:
        """Fetch detailed information for specific trials.
        
        Args:
            nct_ids: List of NCT identifiers (e.g., ['NCT00000001'])
            
        Returns:
            List of trial dictionaries with full details
        """
        if not nct_ids:
            return []
        
        all_trials = []
        
        for nct_id in nct_ids:
            try:
                response = self._make_request(f"studies/{nct_id}", {})
                trial_data = response.json()
                
                parsed_trial = self._parse_trial_data(trial_data)
                if parsed_trial:
                    all_trials.append(parsed_trial)
                
                logger.debug(f"Fetched trial: {nct_id}")
                
            except Exception as e:
                logger.error(f"Failed to fetch trial {nct_id}: {e}")
                continue
        
        logger.info(f"Fetched {len(all_trials)} trial details")
        return all_trials
    
    def _parse_trial_data(self, trial_data: Dict) -> Optional[Dict]:
        """Parse trial data into structured format.
        
        Args:
            trial_data: Raw trial data from API
            
        Returns:
            Parsed trial dictionary
        """
        try:
            protocol = trial_data.get("protocolSection", {})
            identification = protocol.get("identificationModule", {})
            status_module = protocol.get("statusModule", {})
            description = protocol.get("descriptionModule", {})
            conditions = protocol.get("conditionsModule", {})
            design = protocol.get("designModule", {})
            arms = protocol.get("armsInterventionsModule", {})
            outcomes = protocol.get("outcomesModule", {})
            eligibility = protocol.get("eligibilityModule", {})
            contacts = protocol.get("contactsLocationsModule", {})
            
            # Extract key fields
            nct_id = identification.get("nctId", "")
            title = identification.get("officialTitle") or identification.get("briefTitle", "")
            brief_summary = description.get("briefSummary", "")
            detailed_description = description.get("detailedDescription", "")
            
            # Combine summaries
            summary = brief_summary
            if detailed_description:
                summary = f"{brief_summary}\n\n{detailed_description}"
            
            # Extract conditions
            condition_list = conditions.get("conditions", [])
            
            # Extract interventions
            intervention_list = []
            for intervention in arms.get("interventions", []):
                intervention_list.append({
                    "type": intervention.get("type", ""),
                    "name": intervention.get("name", ""),
                    "description": intervention.get("description", "")
                })
            
            # Extract outcomes
            primary_outcomes = outcomes.get("primaryOutcomes", [])
            secondary_outcomes = outcomes.get("secondaryOutcomes", [])
            
            # Extract phases
            phases = design.get("phases", [])
            
            # Extract enrollment
            enrollment_info = design.get("enrollmentInfo", {})
            enrollment_count = enrollment_info.get("count", 0)
            
            # Extract status
            overall_status = status_module.get("overallStatus", "")
            start_date = status_module.get("startDateStruct", {}).get("date", "")
            completion_date = status_module.get("completionDateStruct", {}).get("date", "")
            
            # Extract sponsor
            sponsor_info = protocol.get("sponsorCollaboratorsModule", {})
            lead_sponsor = sponsor_info.get("leadSponsor", {}).get("name", "")
            
            # Extract locations
            locations = []
            for location in contacts.get("locations", []):
                facility = location.get("facility", "")
                city = location.get("city", "")
                country = location.get("country", "")
                if facility or city:
                    locations.append(f"{facility}, {city}, {country}".strip(", "))
            
            return {
                "nct_id": nct_id,
                "title": title,
                "summary": summary,
                "conditions": condition_list,
                "interventions": intervention_list,
                "primary_outcomes": primary_outcomes,
                "secondary_outcomes": secondary_outcomes,
                "phases": phases,
                "enrollment": enrollment_count,
                "status": overall_status,
                "start_date": start_date,
                "completion_date": completion_date,
                "sponsor": lead_sponsor,
                "locations": locations,
                "source": "clinicaltrials"
            }
            
        except Exception as e:
            logger.error(f"Error parsing trial data: {e}")
            return None
    
    def search_and_fetch(
        self,
        query: Optional[str] = None,
        condition: Optional[str] = None,
        intervention: Optional[str] = None,
        max_results: int = 100
    ) -> List[Dict]:
        """Combined search and fetch operation.
        
        Args:
            query: General search query
            condition: Specific condition
            intervention: Specific intervention
            max_results: Maximum number of results
            
        Returns:
            List of trial dictionaries with full details
        """
        logger.info(f"Searching ClinicalTrials.gov (max_results={max_results})")
        
        all_trials = []
        page_token = None
        
        while len(all_trials) < max_results:
            page_size = min(100, max_results - len(all_trials))
            
            result = self.search(
                query=query,
                condition=condition,
                intervention=intervention,
                page_size=page_size,
                page_token=page_token
            )
            
            studies = result["studies"]
            if not studies:
                break
            
            # Parse trials directly from search results
            for study in studies:
                parsed = self._parse_trial_data(study)
                if parsed:
                    all_trials.append(parsed)
            
            # Check if there are more pages
            page_token = result.get("next_page_token")
            if not page_token or len(all_trials) >= max_results:
                break
        
        logger.info(f"Successfully fetched {len(all_trials)} clinical trials")
        return all_trials[:max_results]
