"""Unit tests for agent tools"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))

import pytest
from unittest.mock import Mock, patch

def test_call_concierge():
    with patch('concierge_agent.invoke') as mock:
        mock.return_value = 'Career advice here'
        from tools.agent_tools import call_concierge
        result = call_concierge('user123', 'Need career advice', 'sess1')
        
        assert isinstance(result, str)
        assert 'advice' in result.lower()

def test_call_skill_parser():
    with patch('skill_parser_agent.invoke') as mock:
        mock.return_value = '{"skills": ["Python", "AWS"]}'
        from tools.agent_tools import call_skill_parser
        result = call_skill_parser('user123', 'base64pdf')
        
        assert isinstance(result, str)
        assert 'Python' in result

def test_call_job_matcher():
    with patch('job_matcher_agent.invoke') as mock:
        mock.return_value = '{"matches": [{"job_id": "job1", "score": 95}]}'
        from tools.agent_tools import call_job_matcher
        result = call_job_matcher('user123', {'location': 'Tokyo'})
        
        assert isinstance(result, str)
        assert 'job1' in result

def test_call_interviewer():
    with patch('interviewer_copilot_agent.invoke') as mock:
        mock.return_value = '{"questions": ["Tell me about yourself"]}'
        from tools.agent_tools import call_interviewer
        result = call_interviewer('user123', 'int1', 'generate_questions', {})
        
        assert isinstance(result, str)
        assert 'yourself' in result.lower()
