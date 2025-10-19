"""Integration tests for AgentCore Memory with real connections"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agents"))

import pytest
import os
from botocore.exceptions import ClientError

pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    not os.getenv("AWS_REGION"),
    reason="AWS_REGION not configured",
)
def test_memory_client_import():
    """Test AgentCore Memory client import"""
    try:
        from bedrock_agentcore.memory import MemoryClient
        assert MemoryClient is not None
    except ImportError:
        pytest.skip("bedrock_agentcore not installed")


@pytest.mark.skipif(
    not os.getenv("AWS_REGION") or not os.getenv("MEMORY_ID"),
    reason="AWS credentials or Memory ID not configured",
)
def test_create_memory_event_real():
    """Test real AgentCore Memory connection"""
    from tools.memory_tools import create_memory_event, _memory_tool
    
    # Reset client to ensure no mocks are applied
    _memory_tool._client = None

    try:
        result = create_memory_event(
            memory_id=os.getenv("MEMORY_ID"),
            actor_id="test_user",
            session_id="test_session",
            messages=[("Hello", "user")],
        )
        assert isinstance(result, dict)
        assert "eventId" in result or "event" in str(result)
    except ClientError as e:
        if e.response['Error']['Code'] in ['ResourceNotFoundException', 'ValidationException']:
            pytest.skip(f"Memory not accessible: {e}")
        raise
    except Exception as e:
        if "ResourceNotFoundException" in str(e) or "ValidationException" in str(e):
            pytest.skip(f"Memory not accessible: {e}")
        raise
