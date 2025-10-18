"""Unit tests for collector tools"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))

import pytest
from unittest.mock import Mock, patch
from tools.collector_tools import (
    search_linkedin_profile,
    search_github_profile,
    search_company_info,
    search_job_market
)


def test_search_linkedin_profile():
    from tools.collectors.linkedin import LinkedInCollector
    
    with patch.object(LinkedInCollector, 'collect', return_value={'name': 'John Doe', 'company': 'Tech Corp'}):
        result = search_linkedin_profile('John Doe', 'Tech Corp')
        
        assert result['name'] == 'John Doe'
        assert result['company'] == 'Tech Corp'


def test_search_github_profile():
    from tools.collectors.github import GitHubCollector
    
    with patch.object(GitHubCollector, 'collect', return_value={'username': 'johndoe', 'repos': 50}):
        result = search_github_profile('johndoe')
        
        assert result['username'] == 'johndoe'
        assert result['repos'] == 50


def test_search_company_info():
    from tools.collectors.company import CompanySearchCollector
    
    with patch.object(CompanySearchCollector, 'collect', return_value={'name': 'Tech Corp', 'industry': 'Software'}):
        result = search_company_info('Tech Corp')
        
        assert result['name'] == 'Tech Corp'
        assert result['industry'] == 'Software'


def test_search_job_market():
    from tools.collectors.job_market import JobMarketSearchCollector
    
    with patch.object(JobMarketSearchCollector, 'collect', return_value=[{'title': 'Engineer', 'location': 'Tokyo'}]):
        result = search_job_market('Engineer', 'Tokyo')
        
        assert len(result) == 1
        assert result[0]['title'] == 'Engineer'
