"""Candidate search collector (personal information only)"""

from typing import Dict
from .base import BaseBrowserCollector


class CandidateSearchCollector(BaseBrowserCollector):
    """Search for candidate's personal online presence"""

    SYSTEM_PROMPT = "Display search results for candidate."

    def collect(self, candidate_name: str, **context) -> Dict:
        """Search for candidate's personal information

        Args:
            candidate_name: Full name of candidate
            **context: Additional context (company, job_title, location, etc.)

        Returns:
            Dict with search result URLs for personal profiles
        """
        return self.search(candidate_name, **context)

    def search(self, candidate_name: str, company: str = None, job_title: str = None, 
               location: str = None, **kwargs) -> Dict:
        """Search for candidate's personal information with context
        
        Args:
            candidate_name: Full name of candidate
            company: Current company (helps identify correct person)
            job_title: Job title (helps identify correct person)
            location: Location (helps identify correct person)
        """
        # Build search query with context
        search_terms = [candidate_name]
        if company:
            search_terms.append(company)
        if job_title:
            search_terms.append(job_title)
        if location:
            search_terms.append(location)
        
        search_query = " ".join(search_terms)
        
        prompt = f"""
        Search for candidate: {search_query}
        
        Return JSON with personal profile search URLs:
        {{
            "candidate_name": "{candidate_name}",
            "search_context": "{search_query}",
            "linkedin_profile_search": "LinkedIn profile search URL",
            "github_profile_search": "GitHub profile search URL",
            "google_search_url": "Google search URL",
            "note": "Search for candidate's personal profiles with context to identify correct person"
        }}
        
        Use: https://www.google.com/search?q={search_query.replace(' ', '+')}
        """

        result = self._scrape_with_browser(prompt)

        if isinstance(result, dict):
            return result

        return {
            "candidate_name": candidate_name,
            "search_context": search_query,
            "note": "Search results available for candidate's personal information",
        }
