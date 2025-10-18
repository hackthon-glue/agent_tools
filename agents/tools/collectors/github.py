"""GitHub data collector (optional API usage)"""

from typing import Dict, Optional
import requests


class GitHubCollector:
    """Collect GitHub data (API optional, username validation fallback)"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.github.com"

    def collect(self, github_username: str) -> Dict:
        """Collect GitHub profile data
        
        Args:
            github_username: GitHub username provided by candidate
            
        Returns:
            Dict with profile data (API if available, validation otherwise)
        """
        # If API key provided, use GitHub API
        if self.api_key:
            return self._collect_via_api(github_username)
        
        # Otherwise, just validate username
        return self._validate_username(github_username)

    def _collect_via_api(self, github_username: str) -> Dict:
        """Collect via GitHub API (if API key provided)"""
        try:
            headers = {"Authorization": f"token {self.api_key}"}
            
            # Get user profile
            user_response = requests.get(
                f"{self.base_url}/users/{github_username}",
                headers=headers,
                timeout=10
            )
            
            if user_response.status_code != 200:
                return self._validate_username(github_username)
            
            user_data = user_response.json()
            
            # Get repositories
            repos_response = requests.get(
                f"{self.base_url}/users/{github_username}/repos",
                headers=headers,
                params={"sort": "updated", "per_page": 10},
                timeout=10
            )
            
            repos = repos_response.json() if repos_response.status_code == 200 else []
            
            languages = set()
            repositories = []
            for repo in repos[:10]:
                if repo.get("language"):
                    languages.add(repo["language"])
                repositories.append({
                    "name": repo.get("name"),
                    "description": repo.get("description"),
                    "stars": repo.get("stargazers_count", 0),
                    "language": repo.get("language")
                })
            
            return {
                "username": github_username,
                "name": user_data.get("name"),
                "bio": user_data.get("bio"),
                "location": user_data.get("location"),
                "public_repos": user_data.get("public_repos", 0),
                "followers": user_data.get("followers", 0),
                "repositories": repositories,
                "top_languages": list(languages),
                "profile_url": user_data.get("html_url"),
                "data_source": "GitHub API"
            }
            
        except Exception as e:
            return {
                "username": github_username,
                "error": f"API error: {str(e)}",
                "fallback": self._validate_username(github_username)
            }

    def _validate_username(self, github_username: str) -> Dict:
        """Validate GitHub username (no API)"""
        if not github_username:
            return {"valid": False, "error": "No username provided"}
        
        return {
            "valid": True,
            "username": github_username,
            "profile_url": f"https://github.com/{github_username}",
            "data_source": "Username validation only",
            "note": "Provide API key for full data access"
        }
