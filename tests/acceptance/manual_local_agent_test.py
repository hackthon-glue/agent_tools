"""Manual local agent testing script - NOT a pytest test

Usage: python manual_local_agent_test.py

This script directly invokes agents locally without AgentCore Runtime deployment.
Use for development and debugging individual agents.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agents"))


class MockContext:
    def __init__(self, session_id="test_session"):
        self.session_id = session_id


def test_concierge():
    """Test Concierge Agent locally"""
    print("\n" + "=" * 60)
    print("Testing Concierge Agent")
    print("=" * 60)
    from concierge_agent import invoke

    payload = {
        "user_id": "user123",
        "message": "I'm looking for a software engineer role in Tokyo",
        "action": "job_search",
    }
    context = MockContext(session_id="test_session")

    result = invoke(payload, context)
    print(f"\n📥 Response:\n{result}")
    print("\n✅ Concierge test completed")


def test_skill_parser():
    """Test Skill Parser Agent locally"""
    print("\n" + "=" * 60)
    print("Testing Skill Parser Agent")
    print("=" * 60)
    from skill_parser_agent import invoke

    payload = {"user_id": "user123", "resume_pdf": None}
    context = MockContext()

    result = invoke(payload, context)
    print(f"\n📥 Response:\n{result}")
    print("\n✅ Skill parser test completed")


def test_job_matcher():
    """Test Job Matcher Agent locally"""
    print("\n" + "=" * 60)
    print("Testing Job Matcher Agent")
    print("=" * 60)
    from job_matcher_agent import invoke

    payload = {"user_id": "user123", "filters": {"location": "Tokyo"}}
    context = MockContext()

    result = invoke(payload, context)
    print(f"\n📥 Response:\n{result}")
    print("\n✅ Job matcher test completed")


def test_interviewer():
    """Test Interviewer Copilot Agent locally"""
    print("\n" + "=" * 60)
    print("Testing Interviewer Copilot Agent")
    print("=" * 60)
    from interviewer_copilot_agent import invoke

    payload = {
        "user_id": "user123",
        "interview_id": "int_test",
        "action": "generate_questions",
    }
    context = MockContext()

    result = invoke(payload, context)
    print(f"\n📥 Response:\n{result}")
    print("\n✅ Interviewer test completed")


def test_orchestrator():
    """Test Orchestrator Agent locally"""
    print("\n" + "=" * 60)
    print("Testing Orchestrator Agent")
    print("=" * 60)
    from orchestrator_agent import invoke

    payload = {
        "user_id": "user123",
        "request": "I'm looking for a job in Tokyo",
        "session_id": "orch_test",
    }
    context = MockContext(session_id="orch_test")

    result = invoke(payload, context)
    print(f"\n📥 Response:\n{result}")
    print("\n✅ Orchestrator test completed")


if __name__ == "__main__":
    import os

    print("\n🚀 Manual Local Agent Testing")
    print("=" * 60)
    print("Purpose: Test agents locally without AgentCore Runtime")
    print("Prerequisites:")
    print("  - AWS credentials configured")
    print("  - DynamoDB tables created (optional)")
    print("  - AgentCore Memory configured (optional)")
    print("=" * 60)

    if not os.getenv("AWS_REGION"):
        print("\n⚠️  Warning: AWS_REGION not set")
        print("Set with: export AWS_REGION=us-west-2")

    try:
        test_orchestrator()
        test_concierge()
        test_skill_parser()
        test_job_matcher()
        test_interviewer()
        print("\n" + "=" * 60)
        print("✅ All manual tests completed")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
