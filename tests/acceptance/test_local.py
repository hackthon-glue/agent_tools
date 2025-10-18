"""Local testing script for agents"""

import sys
import pytest

sys.path.insert(0, "agents")


@pytest.mark.acceptance
@pytest.mark.skipif(
    True,
    reason="Requires valid AWS credentials - run manually with: pytest -m acceptance",
)
def test_concierge():
    """Test Concierge Agent locally"""
    print("\n=== Testing Concierge Agent ===")
    from agents.concierge_agent import invoke

    result = invoke(
        {
            "user_id": "user123",
            "message": "I'm looking for a software engineer role in Tokyo",
            "session_id": "test_session",
        }
    )
    print(f"Response: {result.get('response', 'No response')[:200]}")
    print(f"Session ID: {result.get('session_id')}")


def test_skill_parser():
    """Test Skill Parser Agent locally"""
    print("\n=== Testing Skill Parser Agent ===")
    from agents.skill_parser_agent import invoke

    result = invoke(
        {"user_id": "user123", "resume_pdf": None}  # Would be base64 PDF in production
    )
    print(f"Analysis: {str(result.get('analysis', 'No analysis'))[:200]}")


def test_job_matcher():
    """Test Job Matcher Agent locally"""
    print("\n=== Testing Job Matcher Agent ===")
    from agents.job_matcher_agent import invoke

    result = invoke({"user_id": "user123", "filters": {"location": "Tokyo"}})
    print(f"Matches: {str(result.get('matches', 'No matches'))[:200]}")


def test_interviewer():
    """Test Interviewer Copilot Agent locally"""
    print("\n=== Testing Interviewer Copilot Agent ===")
    from agents.interviewer_copilot_agent import invoke

    result = invoke(
        {
            "user_id": "user123",
            "interview_id": "int_test",
            "action": "generate_questions",
        }
    )
    print(f"Response: {result.get('response', 'No response')[:200]}")
    print(f"Context: {result.get('context_summary')}")


def test_orchestrator():
    """Test Orchestrator Agent locally"""
    print("\n=== Testing Orchestrator Agent ===")
    from agents.orchestrator_agent import invoke

    result = invoke(
        {
            "user_id": "user123",
            "request": "I'm looking for a job in Tokyo",
            "session_id": "orch_test",
        }
    )
    print(f"Response: {result.get('response', 'No response')[:200]}")


if __name__ == "__main__":
    print("Starting local agent tests...")
    print("Note: Ensure AWS credentials and DynamoDB tables are configured")

    try:
        test_orchestrator()
        test_concierge()
        test_skill_parser()
        test_job_matcher()
        test_interviewer()
        print("\n✓ All tests completed")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
