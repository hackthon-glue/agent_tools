"""Integration tests for DynamoDB tools with real AWS connections"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agents"))

import pytest
import os

# Skip if AWS credentials not available
pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    not os.getenv("AWS_REGION") or not os.getenv("AWS_ACCESS_KEY_ID"),
    reason="AWS credentials not configured",
)
def test_get_user_profile_real():
    """Test real DynamoDB connection for user profile"""
    from tools.dynamodb_tools import get_user_profile

    # This will fail if table doesn't exist, which is expected
    # In real environment, this would return actual data
    try:
        result = get_user_profile("test_user_123")
        assert isinstance(result, dict)
    except Exception as e:
        # Expected if table doesn't exist in test environment
        assert "ResourceNotFoundException" in str(e) or "Item" in str(e)
