"""Integration tests for DynamoDB tools with real AWS connections"""

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
def test_dynamodb_connection():
    """Test DynamoDB connection"""
    client = boto3.client('dynamodb', region_name=os.getenv('AWS_REGION'))
    try:
        response = client.list_tables(Limit=1)
        assert 'TableNames' in response
    except ClientError as e:
        pytest.skip(f"AWS credentials not valid: {e}")


@pytest.mark.skipif(
    not os.getenv("AWS_REGION") or not os.getenv("DYNAMODB_USERS_TABLE"),
    reason="AWS credentials or table name not configured",
)
def test_get_user_profile_real():
    """Test real DynamoDB connection for user profile"""
    from tools.dynamodb_tools import get_user_profile

    try:
        result = get_user_profile("test_user_123")
        assert isinstance(result, dict)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            pytest.skip(f"Table not found: {e}")
        raise
