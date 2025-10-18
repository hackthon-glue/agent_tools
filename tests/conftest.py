"""Pytest configuration and fixtures"""

import pytest
from unittest.mock import Mock, patch


@pytest.fixture(autouse=True)
def mock_aws_services():
    """Auto-mock AWS services for all tests"""
    with patch('boto3.client') as mock_boto, \
         patch('bedrock_agentcore.memory.MemoryClient') as mock_memory, \
         patch('agents.tools.memory_tools.get_conversation_history', return_value=[]):
        yield {
            'boto': mock_boto,
            'memory': mock_memory
        }
