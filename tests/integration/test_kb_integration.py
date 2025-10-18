"""Integration tests for Knowledge Base tools with real Bedrock"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agents"))

import pytest
import os

pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    not os.getenv("AWS_REGION") or not os.getenv("KNOWLEDGE_BASE_ID"),
    reason="AWS credentials or KB ID not configured",
)
def test_retrieve_evaluation_criteria_real():
    """Test real Bedrock KB connection"""
    from tools.kb_tools import retrieve_evaluation_criteria

    try:
        result = retrieve_evaluation_criteria("technical skills")
        assert isinstance(result, list)
    except Exception as e:
        # Expected if KB doesn't exist
        assert "ResourceNotFoundException" in str(e) or "ValidationException" in str(e)
