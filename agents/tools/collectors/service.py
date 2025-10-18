"""Unified recruitment data collection service"""

from typing import Dict, Optional
from datetime import datetime
from .candidate_search import CandidateSearchCollector
from .linkedin import LinkedInCollector
from .github import GitHubCollector
from .company import CompanySearchCollector
from .job_market import JobMarketSearchCollector


class RecruitmentDataCollectionService:
    """Unified service for recruitment data collection"""

    def __init__(
        self,
        region: str = "us-west-2",
        github_api_key: Optional[str] = None,
        linkedin_api_key: Optional[str] = None,
    ):
        self.region = region
        self.github_api_key = github_api_key
        self.linkedin_api_key = linkedin_api_key

    def get_linkedin_profile(self, linkedin_url: str) -> Dict:
        """Get LinkedIn profile"""
        print(f"\n🔗 Processing LinkedIn profile...")
        return LinkedInCollector(self.linkedin_api_key).collect(linkedin_url)

    def get_github_profile(self, github_username: str) -> Dict:
        """Get GitHub profile"""
        print(f"\n💻 Processing GitHub profile...")
        return GitHubCollector(self.github_api_key).collect(github_username)

    def search_candidate(self, candidate_name: str) -> Dict:
        """Search for candidate's personal information

        Args:
            candidate_name: Full name of candidate

        Returns:
            Dict with search URLs for candidate's personal profiles
        """
        print(f"\n🔍 Searching for {candidate_name}...")
        return CandidateSearchCollector(self.region).search(candidate_name)

    def search_company(self, company_name: str) -> Dict:
        """Search for company information

        Args:
            company_name: Company name

        Returns:
            Dict with search URLs for company information
        """
        print(f"\n🏢 Searching company information for {company_name}...")
        return CompanySearchCollector(self.region).search(company_name)

    def search_job_market(self, job_title: str, location: Optional[str] = None) -> Dict:
        """Search job market information"""
        print(f"\n📊 Searching job market...")
        return JobMarketSearchCollector(self.region).search(job_title, location)

    def collect_candidate_info(
        self,
        candidate_name: str,
        linkedin_url: Optional[str] = None,
        github_username: Optional[str] = None,
        company: Optional[str] = None,
    ) -> Dict:
        """Collect candidate information

        Args:
            candidate_name: Full name of candidate
            linkedin_url: Optional LinkedIn profile URL
            github_username: Optional GitHub username
            company: Optional company name (for company search)

        Returns:
            Dict with candidate personal info and company info separately
        """
        print(f"\n🔍 Collecting information for {candidate_name}...")

        result = {
            "candidate_name": candidate_name,
            "collection_timestamp": datetime.now().isoformat(),
            "api_status": {
                "github": "enabled" if self.github_api_key else "disabled",
                "linkedin": "enabled" if self.linkedin_api_key else "disabled",
            },
        }

        # Candidate personal information
        if linkedin_url:
            result["linkedin"] = self.get_linkedin_profile(linkedin_url)

        if github_username:
            result["github"] = self.get_github_profile(github_username)

        result["candidate_search"] = self.search_candidate(candidate_name)

        # Company information (separate from candidate)
        if company:
            result["company_info"] = self.search_company(company)

        return result


def collect_candidate_data(
    candidate_name: str,
    linkedin_url: Optional[str] = None,
    github_username: Optional[str] = None,
    company: Optional[str] = None,
    region: str = "us-west-2",
    github_api_key: Optional[str] = None,
    linkedin_api_key: Optional[str] = None,
    **kwargs,
) -> Dict:
    """Convenience function for candidate data collection"""
    return RecruitmentDataCollectionService(
        region=region, github_api_key=github_api_key, linkedin_api_key=linkedin_api_key
    ).collect_candidate_info(
        candidate_name, linkedin_url, github_username, company, **kwargs
    )
