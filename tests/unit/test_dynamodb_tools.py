"""Unit tests for DynamoDB tools"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agents"))

import pytest
from unittest.mock import Mock, patch
from tools.dynamodb_tools import get_user_profile, get_job_listings, get_github_profile


@pytest.fixture
def mock_dynamodb():
    with patch('boto3.resource') as mock:
        table = Mock()
        mock.return_value.Table.return_value = table
        yield table

# Note: Tests now mock at execute level instead of boto3 level


def test_get_user_profile(mock_dynamodb):
    from tools.dynamodb_tools import _dynamodb_tool
    
    with patch.object(_dynamodb_tool, 'execute', return_value={'user_id': 'user123', 'name': 'Taro Yamada', 'skills': ['Python']}):
        result = get_user_profile('user123')
        
        assert result['user_id'] == 'user123'
        assert result['name'] == 'Taro Yamada'


def test_get_job_listings_no_filters(mock_dynamodb):
    from tools.dynamodb_tools import _dynamodb_tool
    
    with patch.object(_dynamodb_tool, 'execute', return_value=[{'job_id': 'job1', 'title': 'Engineer'}]):
        result = get_job_listings()
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['job_id'] == 'job1'


def test_get_job_listings_with_filters(mock_dynamodb):
    from tools.dynamodb_tools import _dynamodb_tool
    
    with patch.object(_dynamodb_tool, 'execute', return_value=[{'job_id': 'job1', 'location': 'Tokyo'}]):
        result = get_job_listings({'location': 'Tokyo'})
        
        assert isinstance(result, list)
        assert len(result) == 1


def test_get_github_profile(mock_dynamodb):
    from tools.dynamodb_tools import _dynamodb_tool
    
    with patch.object(_dynamodb_tool, 'execute', return_value={'user_id': 'user123', 'username': 'testuser', 'repos': 10}):
        result = get_github_profile('user123')
        
        assert isinstance(result, dict)
        assert result.get('username') == 'testuser'
