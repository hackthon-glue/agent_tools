"""Pytest configuration and fixtures"""

import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch
from dotenv import load_dotenv

# Load .env file for integration tests
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


@pytest.fixture(autouse=True)
def mock_aws_services(request):
    """Auto-mock AWS services for unit tests only"""
    # Skip mocking for integration and acceptance tests
    test_path = str(request.fspath)
    if "integration" in test_path or "acceptance" in test_path:
        yield {}
        return
    
    # Also check markers
    for marker in request.node.iter_markers():
        if marker.name in ["integration", "acceptance"]:
            yield {}
            return
    
    with patch('boto3.client') as mock_boto, \
         patch('bedrock_agentcore.memory.MemoryClient') as mock_memory, \
         patch('agents.tools.memory_tools.get_conversation_history', return_value=[]):
        yield {
            'boto': mock_boto,
            'memory': mock_memory
        }
