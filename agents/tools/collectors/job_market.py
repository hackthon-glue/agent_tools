"""Job market search collector (search only, no scraping)"""

from typing import Dict
from .base import BaseBrowserCollector


class JobMarketSearchCollector(BaseBrowserCollector):
    """Search job market information (display search results only)"""

    SYSTEM_PROMPT = "Display job market search results."

    def collect(self, job_title: str, location: str = None) -> Dict:
        """Collect job market information"""
        return self.search(job_title, location)

    def search(self, job_title: str, location: str = None) -> Dict:
        """Search job market information
        
        Args:
            job_title: Job title or role
            location: Optional location filter
            
        Returns:
            Dict with search result URLs (no data extraction)
        """
        search_query = job_title
        if location:
            search_query += f" {location}"

        prompt = f"""
        Search job market for: {search_query}
        
        Return JSON with search URLs only (do not extract job data):
        {{
            "job_title": "{job_title}",
            "location": "{location or 'global'}",
            "linkedin_jobs_url": "LinkedIn Jobs search URL",
            "indeed_search_url": "Indeed search URL",
            "glassdoor_search_url": "Glassdoor search URL",
            "note": "HR should review current market trends from official job sites"
        }}
        
        Use: https://www.google.com/search?q={search_query.replace(' ', '+')}+jobs
        """

        result = self._scrape_with_browser(prompt)
        
        if isinstance(result, dict):
            return result
        
        return {
            "job_title": job_title,
            "location": location or "global",
            "note": "Search results available - HR should review official job sites"
        }
