"""AgentCore data collection test"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from collectors import (
    CandidateSearchCollector,
    CompanySearchCollector,
    JobMarketSearchCollector,
    GitHubCollector,
    LinkedInCollector,
)

CANDIDATE = "Shota Hirabayashi"
COMPANY = "Accenture"
JOB = "Software Engineer"
LOCATION = "Japan"


def test_candidate_search():
    """Test candidate search with AgentCore Browser"""
    print("\n" + "=" * 60)
    print("TEST: Candidate Search (AgentCore Browser)")
    print("=" * 60)

    collector = CandidateSearchCollector(region="us-west-2")
    result = collector.search(CANDIDATE)

    print(f"✅ Candidate: {result.get('candidate_name')}")
    print(f"🔗 LinkedIn Search: {result.get('linkedin_profile_search', 'N/A')}")
    print(f"💻 GitHub Search: {result.get('github_profile_search', 'N/A')}")
    print(f"🌐 Google Search: {result.get('google_search_url', 'N/A')}")

    assert result.get("candidate_name") == CANDIDATE
    assert "note" in result or "linkedin_profile_search" in result


def test_company_search():
    """Test company search with AgentCore Browser"""
    print("\n" + "=" * 60)
    print("TEST: Company Search (AgentCore Browser)")
    print("=" * 60)

    collector = CompanySearchCollector(region="us-west-2")
    result = collector.search(COMPANY)

    print(f"✅ Company: {result.get('company_name')}")
    print(f"🏢 Glassdoor: {result.get('glassdoor_search_url', 'N/A')}")
    print(f"🔗 LinkedIn: {result.get('linkedin_company_url', 'N/A')}")
    print(f"🌐 Website: {result.get('company_website_url', 'N/A')}")

    assert result.get("company_name") == COMPANY
    assert "note" in result or "glassdoor_search_url" in result


def test_job_market_search():
    """Test job market search with AgentCore Browser"""
    print("\n" + "=" * 60)
    print("TEST: Job Market Search (AgentCore Browser)")
    print("=" * 60)

    collector = JobMarketSearchCollector(region="us-west-2")
    result = collector.search(JOB, LOCATION)

    print(f"✅ Job Title: {result.get('job_title')}")
    print(f"📍 Location: {result.get('location')}")
    print(f"🔗 LinkedIn Jobs: {result.get('linkedin_jobs_url', 'N/A')}")
    print(f"🔍 Indeed: {result.get('indeed_search_url', 'N/A')}")

    assert result.get("job_title") == JOB
    assert result.get("location") == LOCATION


def test_github_api():
    """Test GitHub API (if key available)"""
    print("\n" + "=" * 60)
    print("TEST: GitHub API")
    print("=" * 60)

    api_key = os.getenv("GITHUB_API_KEY") or os.getenv("GITHUB_TOKEN")
    collector = GitHubCollector(api_key)
    result = collector.collect("torvalds")

    if api_key:
        print(f"✅ Username: {result.get('username')}")
        print(f"👤 Name: {result.get('name', 'N/A')}")
        print(f"📦 Repos: {result.get('public_repos', 0)}")
        print(f"💻 Languages: {result.get('top_languages', [])[:3]}")
        assert result.get("username") == "torvalds"
    else:
        print(f"⚠️  No API key - validation only")
        print(f"✅ Valid: {result.get('valid')}")
        print(f"🔗 Profile: {result.get('profile_url')}")
        assert result.get("valid") == True


def test_linkedin_validation():
    """Test LinkedIn URL validation"""
    print("\n" + "=" * 60)
    print("TEST: LinkedIn URL Validation")
    print("=" * 60)

    api_key = os.getenv("LINKEDIN_API_KEY")
    collector = LinkedInCollector(api_key)
    result = collector.collect("https://www.linkedin.com/in/shotahirabayashi/")

    if api_key:
        print(f"✅ API enabled")
        print(f"🔗 URL: {result.get('linkedin_url', 'N/A')}")
    else:
        print(f"⚠️  No API key - validation only")
        print(f"✅ Valid: {result.get('valid')}")
        print(f"🔗 URL: {result.get('linkedin_url')}")
        print(f"👤 Username: {result.get('username')}")
        assert result.get("valid") == True


def check_aws_setup():
    """Check AWS credentials and provide setup guidance"""
    import subprocess
    try:
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ AWS credentials configured")
            return True
        else:
            print("⚠️  AWS credentials not configured")
            return False
    except:
        print("⚠️  AWS CLI not found or credentials not configured")
        return False


if __name__ == "__main__":
    print("\n🚀 AgentCore Data Collection Test")
    print("=" * 60)

    # Check AWS setup
    aws_ok = check_aws_setup()
    if not aws_ok:
        print("\n⚠️  AgentCore Browser requires AWS setup:")
        print("   1. Install AWS CLI: https://aws.amazon.com/cli/")
        print("   2. Configure credentials: aws configure")
        print("   3. Set IAM permissions for bedrock-agentcore and bedrock:InvokeModel")
        print("   4. Enable Claude Sonnet 4.0 in Bedrock console")
        print("\n   Browser-based tests will fail, but API tests will run.\n")

    try:
        test_candidate_search()
        test_company_search()
        test_job_market_search()
        test_github_api()
        test_linkedin_validation()

        print("\n" + "=" * 60)
        print("✅ All AgentCore tests passed!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        if not aws_ok:
            print("\n💡 Tip: Configure AWS credentials to enable browser-based collectors")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if not aws_ok:
            print("\n💡 Tip: Configure AWS credentials to enable browser-based collectors")
        import traceback
        traceback.print_exc()
        sys.exit(1)
