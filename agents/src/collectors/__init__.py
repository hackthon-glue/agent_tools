"""Recruitment data collectors"""

from .base import BaseBrowserCollector
from .candidate_search import CandidateSearchCollector
from .linkedin import LinkedInCollector
from .github import GitHubCollector
from .company import CompanySearchCollector
from .job_market import JobMarketSearchCollector
from .personal_activities import PersonalActivitiesCollector
from .service import RecruitmentDataCollectionService, collect_candidate_data

__all__ = [
    "BaseBrowserCollector",
    "CandidateSearchCollector",
    "LinkedInCollector",
    "GitHubCollector",
    "CompanySearchCollector",
    "JobMarketSearchCollector",
    "PersonalActivitiesCollector",
    "RecruitmentDataCollectionService",
    "collect_candidate_data",
]
