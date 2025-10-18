"""Acceptance test for RecruitmentDataCollectionService (Agent Tool)"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from collectors import RecruitmentDataCollectionService, collect_candidate_data

# Test candidate information
CANDIDATE = "Shota Hirabayashi"
COMPANY = "Accenture"
JOB = "Software Engineer"
LOCATION = "Japan"
LINKEDIN_URL = "https://www.linkedin.com/in/shotahirabayashi"
GITHUB_USERNAME = "shotahirabayashi"


def test_service_full_workflow():
    """Test complete candidate data collection workflow"""
    print("\n" + "=" * 60)
    print("ACCEPTANCE TEST: Full Candidate Data Collection")
    print("=" * 60)
    
    service = RecruitmentDataCollectionService(
        region="us-west-2",
        github_api_key=os.getenv("GITHUB_API_KEY"),
        linkedin_api_key=os.getenv("LINKEDIN_API_KEY")
    )
    
    result = service.collect_candidate_info(
        candidate_name=CANDIDATE,
        linkedin_url=LINKEDIN_URL,
        github_username=GITHUB_USERNAME,
        company=COMPANY,
        job_title=JOB,
        location=LOCATION
    )
    
    # Verify structure
    assert "candidate_name" in result
    assert result["candidate_name"] == CANDIDATE
    assert "collection_timestamp" in result
    assert "api_status" in result
    assert "search_context" in result
    assert "linkedin" in result
    assert "github" in result
    assert "candidate_search" in result
    assert "personal_activities" in result
    assert "company_info" in result
    
    print(f"\n✅ Candidate: {result['candidate_name']}")
    print(f"🏢 Company: {result.get('search_context', {}).get('company', 'N/A')}")
    print(f"💼 Job Title: {result.get('search_context', {}).get('job_title', 'N/A')}")
    print(f"📍 Location: {result.get('search_context', {}).get('location', 'N/A')}")
    print(f"⏰ Timestamp: {result['collection_timestamp']}")
    print(f"📊 API Status: {result['api_status']}")
    print(f"🔗 LinkedIn: {bool(result['linkedin'])}")
    print(f"💻 GitHub: {bool(result['github'])}")
    print(f"🔍 Candidate Search: {bool(result['candidate_search'])}")
    print(f"🌟 Personal Activities: {bool(result['personal_activities'])}")
    print(f"🏢 Company Info: {bool(result['company_info'])}")


def test_convenience_function():
    """Test convenience function for agents"""
    print("\n" + "=" * 60)
    print("ACCEPTANCE TEST: Convenience Function")
    print("=" * 60)
    
    result = collect_candidate_data(
        candidate_name=CANDIDATE,
        linkedin_url=LINKEDIN_URL,
        github_username=GITHUB_USERNAME,
        company=COMPANY,
        job_title=JOB,
        location=LOCATION
    )
    
    assert result["candidate_name"] == CANDIDATE
    assert "linkedin" in result
    assert "github" in result
    assert "candidate_search" in result
    assert "personal_activities" in result
    assert "company_info" in result
    
    print(f"\n✅ Candidate: {result['candidate_name']}")
    print(f"✅ All data collected successfully")


def test_individual_methods():
    """Test individual service methods"""
    print("\n" + "=" * 60)
    print("ACCEPTANCE TEST: Individual Methods")
    print("=" * 60)
    
    service = RecruitmentDataCollectionService(region="us-west-2")
    
    # Test LinkedIn
    linkedin = service.get_linkedin_profile("https://www.linkedin.com/in/test")
    assert "valid" in linkedin or "linkedin_url" in linkedin
    print(f"✅ LinkedIn: {bool(linkedin)}")
    
    # Test GitHub
    github = service.get_github_profile("torvalds")
    assert "username" in github or "valid" in github
    print(f"✅ GitHub: {bool(github)}")
    
    # Test Candidate Search
    candidate = service.search_candidate(CANDIDATE, company=COMPANY, job_title=JOB, location=LOCATION)
    assert "candidate_name" in candidate
    assert candidate["candidate_name"] == CANDIDATE
    print(f"✅ Candidate Search: {bool(candidate)}")
    
    # Test Personal Activities
    activities = service.search_personal_activities(CANDIDATE, company=COMPANY, job_title=JOB)
    assert "candidate_name" in activities
    print(f"✅ Personal Activities: {bool(activities)}")
    
    # Test Company Search
    company = service.search_company(COMPANY)
    assert "company_name" in company
    assert company["company_name"] == COMPANY
    print(f"✅ Company Search: {bool(company)}")
    
    # Test Job Market Search
    jobs = service.search_job_market(JOB, LOCATION)
    assert "job_title" in jobs
    assert jobs["job_title"] == JOB
    print(f"✅ Job Market Search: {bool(jobs)}")


def test_minimal_input():
    """Test with minimal required input"""
    print("\n" + "=" * 60)
    print("ACCEPTANCE TEST: Minimal Input")
    print("=" * 60)
    
    result = collect_candidate_data(candidate_name=CANDIDATE)
    
    assert result["candidate_name"] == CANDIDATE
    assert "candidate_search" in result
    assert "collection_timestamp" in result
    
    print(f"✅ Candidate: {result['candidate_name']}")
    print(f"✅ Minimal data collected successfully")


def test_api_status_tracking():
    """Test API status tracking"""
    print("\n" + "=" * 60)
    print("ACCEPTANCE TEST: API Status Tracking")
    print("=" * 60)
    
    # Without API keys
    service_no_api = RecruitmentDataCollectionService()
    result_no_api = service_no_api.collect_candidate_info(CANDIDATE)
    
    assert result_no_api["api_status"]["github"] == "disabled"
    assert result_no_api["api_status"]["linkedin"] == "disabled"
    print(f"✅ No API: {result_no_api['api_status']}")
    
    # With API keys (if available)
    github_key = os.getenv("GITHUB_API_KEY")
    linkedin_key = os.getenv("LINKEDIN_API_KEY")
    
    if github_key or linkedin_key:
        service_with_api = RecruitmentDataCollectionService(
            github_api_key=github_key,
            linkedin_api_key=linkedin_key
        )
        result_with_api = service_with_api.collect_candidate_info(CANDIDATE)
        
        if github_key:
            assert result_with_api["api_status"]["github"] == "enabled"
        if linkedin_key:
            assert result_with_api["api_status"]["linkedin"] == "enabled"
        
        print(f"✅ With API: {result_with_api['api_status']}")
    else:
        print(f"⚠️  No API keys - skipped API enabled test")


if __name__ == "__main__":
    print("\n🚀 RecruitmentDataCollectionService Acceptance Tests")
    print("=" * 60)
    print("Testing main tool that agents will call")
    print("=" * 60)
    
    try:
        test_service_full_workflow()
        test_convenience_function()
        test_individual_methods()
        test_minimal_input()
        test_api_status_tracking()
        
        print("\n" + "=" * 60)
        print("✅ All acceptance tests passed!")
        print("=" * 60)
        print("\n📝 Summary:")
        print("- Service can collect full candidate data")
        print("- Convenience function works for agents")
        print("- Individual methods work independently")
        print("- Minimal input is handled correctly")
        print("- API status is tracked properly")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
