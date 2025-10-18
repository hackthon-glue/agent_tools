"""Company information search collector (search only, no scraping)"""

from typing import Dict
from .base import BaseBrowserCollector


class CompanySearchCollector(BaseBrowserCollector):
    """Search for company information (display search results only)"""

    SYSTEM_PROMPT = "Display company information search results."

    def collect(self, company_name: str) -> Dict:
        """Collect company information"""
        return self.search(company_name)

    def search(self, company_name: str) -> Dict:
        """Search for company information
        
        Args:
            company_name: Company name
            
        Returns:
            Dict with search result URLs (no data extraction)
        """
        prompt = f"""
        Search for company: {company_name}
        
        Return JSON with search URLs only (do not extract review data):
        {{
            "company_name": "{company_name}",
            "glassdoor_search_url": "Glassdoor search URL",
            "linkedin_company_url": "LinkedIn company page URL",
            "company_website_url": "Official company website URL",
            "note": "HR should review public information and company official sources"
        }}
        
        Use: https://www.google.com/search?q={company_name.replace(' ', '+')}+company+information
        """

        result = self._scrape_with_browser(prompt)
        
        if isinstance(result, dict):
            return result
        
        return {
            "company_name": company_name,
            "note": "Search results available - HR should verify with official sources"
        }
