"""Collector tools for web data gathering"""

from strands import tool
from typing import Dict, List


@tool
def search_linkedin_profile(candidate_name: str, company: str = None) -> Dict:
    """Search for candidate's LinkedIn profile

    Args:
        candidate_name: Full name of candidate
        company: Optional company name for context

    Returns:
        LinkedIn profile information
    """
    from .collectors import LinkedInCollector

    collector = LinkedInCollector()
    return collector.collect(candidate_name, company=company)


@tool
def search_github_profile(username: str) -> Dict:
    """Search for candidate's GitHub profile

    Args:
        username: GitHub username

    Returns:
        GitHub profile and repository information
    """
    from .collectors import GitHubCollector

    collector = GitHubCollector()
    return collector.collect(username)


@tool
def search_company_info(company_name: str) -> Dict:
    """Search for company information

    Args:
        company_name: Company name

    Returns:
        Company information and details
    """
    from .collectors import CompanySearchCollector

    collector = CompanySearchCollector()
    return collector.collect(company_name)


@tool
def search_job_market(role: str, location: str = None) -> List[Dict]:
    """Search job market for positions

    Args:
        role: Job role or title
        location: Optional location filter

    Returns:
        List of job postings
    """
    from .collectors import JobMarketSearchCollector

    collector = JobMarketSearchCollector()
    return collector.collect(role, location=location)


@tool
def collect_candidate_data(
    candidate_name: str, company: str = None, github_username: str = None
) -> Dict:
    """Collect comprehensive candidate data from multiple sources

    Args:
        candidate_name: Full name of candidate
        company: Optional company name
        github_username: Optional GitHub username

    Returns:
        Comprehensive candidate data
    """
    from .collectors import collect_candidate_data as collect

    return collect(candidate_name, company=company, github_username=github_username)
