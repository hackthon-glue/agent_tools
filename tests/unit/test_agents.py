"""Tests for recruitment agents"""

import pytest
import json
from unittest.mock import Mock, patch

def test_concierge_agent():
    """Test concierge agent conversation"""
    with patch('agents.concierge_agent.agent') as mock_agent:
        mock_agent.return_value.message = {"content": [{"text": "I can help you find suitable positions."}]}
        
        from agents.concierge_agent import invoke
        
        payload = {
            "user_id": "user123",
            "message": "I'm looking for a software engineer role",
            "session_id": "session123"
        }
        context = Mock(session_id="session123")
        
        result = invoke(payload, context)
        
        assert isinstance(result, str)
        assert "help" in result.lower() or "position" in result.lower()

def test_skill_parser_agent():
    """Test skill parsing from resume and GitHub"""
    with patch('agents.skill_parser_agent.agent') as mock_agent:
        mock_response = json.dumps({
            "technical_skills": ["Python", "AWS", "React"],
            "experience_summary": "5 years in backend development",
            "overall_rating": 8
        })
        mock_agent.return_value.message = {"content": [{"text": mock_response}]}
        
        from agents.skill_parser_agent import invoke
        
        payload = {
            "user_id": "user123",
            "resume_pdf": "base64_encoded_pdf"
        }
        context = Mock()
        
        result = invoke(payload, context)
        
        assert isinstance(result, str)

def test_job_matcher_agent():
    """Test job matching logic"""
    with patch('agents.job_matcher_agent.agent') as mock_agent:
        mock_response = json.dumps({
            "matches": [
                {"job_id": "job1", "title": "Senior Engineer", "score": 0.92}
            ],
            "top_match": {"job_id": "job1", "reasons": ["Strong Python skills"]}
        })
        mock_agent.return_value.message = {"content": [{"text": mock_response}]}
        
        from agents.job_matcher_agent import invoke
        
        payload = {
            "user_id": "user123",
            "filters": {"location": "Tokyo"}
        }
        context = Mock()
        
        result = invoke(payload, context)
        
        assert isinstance(result, str)

def test_interviewer_copilot_agent():
    """Test interview question generation"""
    with patch('agents.interviewer_copilot_agent.agent') as mock_agent:
        mock_agent.return_value.message = {"content": [{"text": "1. Explain your experience with microservices"}]}
        
        from agents.interviewer_copilot_agent import invoke
        
        payload = {
            "user_id": "user123",
            "interview_id": "int123",
            "action": "generate_questions"
        }
        context = Mock()
        
        result = invoke(payload, context)
        
        assert isinstance(result, str)
        assert "microservices" in result.lower() or "experience" in result.lower()

@patch('boto3.resource')
def test_get_user_profile(mock_boto):
    """Test user profile retrieval"""
    mock_table = Mock()
    mock_table.get_item.return_value = {
        'Item': {'user_id': 'user123', 'name': 'John Doe'}
    }
    mock_boto.return_value.Table.return_value = mock_table
    
    from agents.tools.dynamodb_tools import get_user_profile
    
    result = get_user_profile("user123")
    
    assert result['user_id'] == 'user123'

def test_get_job_listings():
    """Test job listings retrieval"""
    from agents.tools.dynamodb_tools import get_job_listings, _dynamodb_tool
    
    with patch.object(_dynamodb_tool, 'execute', return_value=[{'job_id': 'job1', 'title': 'Engineer'}]):
        result = get_job_listings()
        
        assert len(result) == 1

def test_retrieve_evaluation_criteria():
    """Test KB retrieval"""
    with patch('agents.tools.kb_tools.boto3.client') as mock_boto, \
         patch('agents.tools.config.ToolConfig.KB_USE_RERANK', False):
        mock_client = Mock()
        mock_client.retrieve.return_value = {
            'retrievalResults': [
                {'content': {'text': 'Criteria 1'}, 'score': 0.9}
            ]
        }
        mock_boto.return_value = mock_client
        
        from agents.tools.kb_tools import retrieve_evaluation_criteria, _kb_tool
        _kb_tool._client = None
        
        result = retrieve_evaluation_criteria("technical skills")
        
        assert len(result) == 1
        assert result[0]['content'] == 'Criteria 1'

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
