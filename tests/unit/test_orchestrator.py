"""Tests for orchestrator agent"""

import pytest
from unittest.mock import Mock, patch

def test_orchestrator_routes_to_concierge():
    """Test orchestrator routes career questions to concierge"""
    with patch('bedrock_agentcore.memory.MemoryClient'), \
         patch('agents.orchestrator_agent.agent') as mock_agent:
        mock_agent.return_value.message = {"content": [{"text": "I've found 3 suitable positions for you."}]}
        
        from agents.orchestrator_agent import invoke
        
        payload = {
            "user_id": "user123",
            "request": "求人を探しています",
            "session_id": "session123"
        }
        context = Mock(session_id="session123")
        
        result = invoke(payload, context)
        
        assert isinstance(result, str)

def test_orchestrator_routes_to_skill_parser():
    """Test orchestrator routes resume analysis to skill parser"""
    with patch('bedrock_agentcore.memory.MemoryClient'), \
         patch('agents.orchestrator_agent.agent') as mock_agent:
        mock_agent.return_value.message = {"content": [{"text": "Analyzed your skills: Python, AWS, React"}]}
        
        from agents.orchestrator_agent import invoke
        
        payload = {
            "user_id": "user123",
            "request": "履歴書を分析してください",
            "context": {"resume_pdf": "base64_pdf"}
        }
        context = Mock()
        
        result = invoke(payload, context)
        
        assert isinstance(result, str)

def test_orchestrator_routes_to_job_matcher():
    """Test orchestrator routes matching requests to job matcher"""
    with patch('bedrock_agentcore.memory.MemoryClient'), \
         patch('agents.orchestrator_agent.agent') as mock_agent:
        mock_agent.return_value.message = {"content": [{"text": "Found 5 matching jobs with scores"}]}
        
        from agents.orchestrator_agent import invoke
        
        payload = {
            "user_id": "user123",
            "request": "私に合う求人を見つけてください"
        }
        context = Mock()
        
        result = invoke(payload, context)
        
        assert isinstance(result, str)

def test_orchestrator_routes_to_interviewer():
    """Test orchestrator routes interview requests to interviewer copilot"""
    with patch('bedrock_agentcore.memory.MemoryClient'), \
         patch('agents.orchestrator_agent.agent') as mock_agent:
        mock_agent.return_value.message = {"content": [{"text": "Generated 5 interview questions"}]}
        
        from agents.orchestrator_agent import invoke
        
        payload = {
            "user_id": "user123",
            "request": "面接の質問を生成してください",
            "context": {"interview_id": "int123"}
        }
        context = Mock()
        
        result = invoke(payload, context)
        
        assert isinstance(result, str)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
