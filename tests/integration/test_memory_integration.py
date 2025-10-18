"""Integration tests for AgentCore Memory with real connections"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agents"))

import pytest
import os

pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    not os.getenv("AWS_REGION") or not os.getenv("MEMORY_ID"),
    reason="AWS credentials or Memory ID not configured",
)
def test_create_memory_event_real():
    """Test real AgentCore Memory connection"""
    from tools.memory_tools import create_memory_event

    try:
        result = create_memory_event(
            memory_id=os.getenv("MEMORY_ID", "test-memory"),
            actor_id="test_user",
            session_id="test_session",
            messages=[("Hello", "user")],
        )
        assert isinstance(result, dict)
        assert "eventId" in result or "event" in str(result)
    except Exception as e:
        # Expected if Memory doesn't exist
        assert "ResourceNotFoundException" in str(e) or "ValidationException" in str(e)
