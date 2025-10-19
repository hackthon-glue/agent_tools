"""Unit tests for PDF tools"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agents"))

import pytest
from unittest.mock import Mock, patch, MagicMock
from tools.pdf_tools import parse_resume, parse_resume_textract


@pytest.fixture
def mock_bedrock():
    with patch('boto3.client') as mock:
        client = Mock()
        body_mock = MagicMock()
        body_mock.read.return_value = '{"content": [{"text": "{\\"name\\": \\"John\\", \\"skills\\": [\\"Python\\"]}"}]}'
        client.invoke_model.return_value = {'body': body_mock}
        mock.return_value = client
        yield client


@pytest.fixture
def mock_textract():
    with patch('boto3.client') as mock:
        client = Mock()
        client.analyze_document.return_value = {
            'Blocks': [
                {'BlockType': 'LINE', 'Text': 'John Doe'},
                {'BlockType': 'LINE', 'Text': 'Python Developer'}
            ]
        }
        mock.return_value = client
        yield client


def test_parse_resume_claude_only(mock_bedrock):
    result = parse_resume('base64pdf', use_textract=False)
    
    assert 'name' in result
    mock_bedrock.invoke_model.assert_called_once()


def test_parse_resume_textract(mock_textract):
    import base64
    # Create valid base64 string
    valid_pdf = base64.b64encode(b'fake pdf content').decode('utf-8')
    result = parse_resume_textract(valid_pdf)
    
    assert 'raw_text' in result
    assert 'John Doe' in result['raw_text']
    assert 'Python Developer' in result['raw_text']
    mock_textract.analyze_document.assert_called_once()
