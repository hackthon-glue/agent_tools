"""Candidate search collector (personal information only)"""

from typing import Dict
from .base import BaseBrowserCollector


class CandidateSearchCollector(BaseBrowserCollector):
    """Search for candidate's personal online presence"""

    SYSTEM_PROMPT = "Display search results for candidate."

    def collect(self, candidate_name: str) -> Dict:
        """Search for candidate's personal information

        Args:
            candidate_name: Full name of candidate

        Returns:
            Dict with search result URLs for personal profiles
        """
        return self.search(candidate_name)

    def search(self, candidate_name: str) -> Dict:
        """Search for candidate's personal information"""
        prompt = f"""
        Search for candidate: {candidate_name}
        
        Return JSON with personal profile search URLs:
        {{
            "candidate_name": "{candidate_name}",
            "linkedin_profile_search": "LinkedIn profile search URL",
            "github_profile_search": "GitHub profile search URL",
            "google_search_url": "Google search URL",
            "note": "Search for candidate's personal profiles and online presence"
        }}
        
        Use: https://www.google.com/search?q={candidate_name.replace(' ', '+')}
        """

        result = self._scrape_with_browser(prompt)

        if isinstance(result, dict):
            return result

        return {
            "candidate_name": candidate_name,
            "note": "Search results available for candidate's personal information",
        }
