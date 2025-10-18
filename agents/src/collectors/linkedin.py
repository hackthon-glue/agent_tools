"""LinkedIn data collector (optional API usage)"""

from typing import Dict, Optional
import requests


class LinkedInCollector:
    """Collect LinkedIn data (API optional, URL validation fallback)"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def collect(self, linkedin_url: str) -> Dict:
        """Collect LinkedIn profile data
        
        Args:
            linkedin_url: LinkedIn profile URL provided by candidate
            
        Returns:
            Dict with profile data (API if available, validation otherwise)
        """
        # If API key provided, use LinkedIn API
        if self.api_key:
            return self._collect_via_api(linkedin_url)
        
        # Otherwise, just validate URL
        return self._validate_url(linkedin_url)

    def _collect_via_api(self, linkedin_url: str) -> Dict:
        """Collect via LinkedIn API (if API key provided)"""
        try:
            # LinkedIn API implementation (placeholder)
            # Note: LinkedIn API requires OAuth and has strict limitations
            return {
                "linkedin_url": linkedin_url,
                "data_source": "LinkedIn API",
                "note": "API implementation required"
            }
        except Exception as e:
            return {
                "linkedin_url": linkedin_url,
                "error": f"API error: {str(e)}",
                "fallback": "URL validation only"
            }

    def _validate_url(self, linkedin_url: str) -> Dict:
        """Validate LinkedIn URL (no API)"""
        import re
        
        if not linkedin_url:
            return {"valid": False, "error": "No URL provided"}
        
        pattern = r'https?://(?:www\.)?linkedin\.com/in/[\w-]+/?'
        if re.match(pattern, linkedin_url):
            username = linkedin_url.rstrip('/').split('/')[-1]
            return {
                "valid": True,
                "linkedin_url": linkedin_url,
                "username": username,
                "data_source": "URL validation only",
                "note": "Provide API key for full data access"
            }
        
        return {
            "valid": False,
            "provided_url": linkedin_url,
            "error": "Invalid LinkedIn URL format"
        }
