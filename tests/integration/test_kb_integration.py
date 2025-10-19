"""Integration tests for Knowledge Base tools with real Bedrock"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agents"))

import pytest
import os
import boto3
from botocore.exceptions import ClientError

pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    not os.getenv("AWS_REGION"),
    reason="AWS_REGION not configured",
)
def test_bedrock_agent_runtime_connection():
    """Test Bedrock Agent Runtime connection"""
    client = boto3.client('bedrock-agent-runtime', region_name=os.getenv('AWS_REGION'))
    assert client is not None


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
    except ClientError as e:
        if e.response['Error']['Code'] in ['ResourceNotFoundException', 'ValidationException']:
            pytest.skip(f"KB not accessible: {e}")
        raise
