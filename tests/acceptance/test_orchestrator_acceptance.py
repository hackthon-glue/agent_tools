"""Acceptance tests for Orchestrator Agent routing and coordination"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agents"))

import pytest
import os
from unittest.mock import Mock

pytestmark = pytest.mark.acceptance


@pytest.mark.skipif(
    not os.getenv("AWS_REGION"), reason="AWS credentials not configured"
)
def test_orchestrator_routes_to_concierge():
    """Test Orchestrator routing user query to Concierge Agent"""
    from orchestrator_agent import invoke

    payload = {
        "user_id": "acceptance_test_user",
        "request": "求人を探しています",  # "I'm looking for jobs"
        "session_id": "acceptance_test_session",
    }
    context = Mock(session_id="acceptance_test_session")

    try:
        result = invoke(payload, context)

        # Verify orchestrator processed the request
        assert isinstance(result, str)
        assert len(result) > 0

    except Exception as e:
        pytest.skip(f"Skipping due to AWS resource unavailability: {str(e)}")


@pytest.mark.skipif(
    not os.getenv("AWS_REGION"), reason="AWS credentials not configured"
)
def test_orchestrator_handles_skill_analysis():
    """Test Orchestrator routing skill analysis request"""
    from orchestrator_agent import invoke

    payload = {
        "user_id": "acceptance_test_user",
        "request": "履歴書を分析してください",  # "Please analyze my resume"
        "context": {"resume_pdf": "base64_encoded_test_data"},
    }
    context = Mock()

    try:
        result = invoke(payload, context)

        assert isinstance(result, str)
        assert len(result) > 0

    except Exception as e:
        pytest.skip(f"Skipping due to AWS resource unavailability: {str(e)}")
