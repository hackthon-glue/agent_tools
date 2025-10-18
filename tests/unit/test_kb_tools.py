"""Unit tests for Knowledge Base tools"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))

import pytest
from unittest.mock import Mock, patch
from tools.kb_tools import retrieve_evaluation_criteria


def test_retrieve_evaluation_criteria():
    with patch('tools.kb_tools.boto3.client') as mock_boto, \
         patch('tools.config.ToolConfig.KB_USE_RERANK', False):
        mock_client = Mock()
        mock_client.retrieve.return_value = {
            'retrievalResults': [
                {
                    'content': {'text': 'Skill matching criteria'},
                    'score': 0.95,
                    'metadata': {'source': 'criteria.pdf'}
                }
            ]
        }
        mock_boto.return_value = mock_client
        
        from tools.kb_tools import _kb_tool
        _kb_tool._client = None
        
        result = retrieve_evaluation_criteria('skill matching')
        
        assert len(result) == 1
        assert result[0]['content'] == 'Skill matching criteria'
        assert result[0]['score'] == 0.95


def test_retrieve_evaluation_criteria_empty():
    with patch('tools.kb_tools.boto3.client') as mock_boto, \
         patch('tools.config.ToolConfig.KB_USE_RERANK', False):
        mock_client = Mock()
        mock_client.retrieve.return_value = {'retrievalResults': []}
        mock_boto.return_value = mock_client
        
        from tools.kb_tools import _kb_tool
        _kb_tool._client = None
        
        result = retrieve_evaluation_criteria('nonexistent')
        
        assert isinstance(result, list)
        assert len(result) == 0
