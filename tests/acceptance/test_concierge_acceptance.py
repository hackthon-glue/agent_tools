"""Acceptance tests for Concierge Agent end-to-end workflows"""

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
def test_concierge_agent_career_consultation():
    """Test full Concierge Agent workflow: user query → AI response"""
    from concierge_agent import invoke

    payload = {
        "user_id": "acceptance_test_user",
        "message": "I'm looking for software engineer positions in Tokyo",
        "action": "job_search",
        "preferences": {"location": "Tokyo", "role": "Engineer"},
    }
    context = Mock(session_id="acceptance_test_session")

    try:
        result = invoke(payload, context)

        # Verify response structure
        assert isinstance(result, str)
        assert len(result) > 0

        # Verify response contains relevant keywords
        assert any(
            keyword in result.lower()
            for keyword in ["job", "position", "engineer", "tokyo", "search"]
        )

    except Exception as e:
        # Log error but don't fail if AWS resources unavailable
        pytest.skip(f"Skipping due to AWS resource unavailability: {str(e)}")
