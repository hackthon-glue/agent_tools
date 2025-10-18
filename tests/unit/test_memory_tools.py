"""Unit tests for memory tools"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))

import pytest
from unittest.mock import Mock, patch
from tools.memory_tools import create_memory_event, get_conversation_history


def test_create_memory_event():
    with patch('bedrock_agentcore.memory.MemoryClient') as mock_client_class:
        mock_client = Mock()
        mock_client.create_event.return_value = {
            'event': {'eventId': 'evt123', 'status': 'created'}
        }
        mock_client_class.return_value = mock_client
        
        from tools.memory_tools import _memory_tool
        _memory_tool._client = None
        
        result = create_memory_event(
            memory_id='mem123',
            actor_id='user1',
            session_id='sess1',
            messages=[('Hello', 'user')]
        )
        
        assert result['eventId'] == 'evt123'
        assert result['status'] == 'created'
        mock_client.create_event.assert_called_once()


def test_get_conversation_history():
    with patch('bedrock_agentcore.memory.MemoryClient') as mock_client_class:
        mock_client = Mock()
        expected_result = [
            [
                {'role': 'user', 'content': {'text': 'Hello'}},
                {'role': 'assistant', 'content': {'text': 'Hi there'}}
            ]
        ]
        mock_client.get_last_k_turns.return_value = expected_result
        mock_client_class.return_value = mock_client
        
        from tools.memory_tools import _memory_tool
        _memory_tool._client = None
        
        result = get_conversation_history(
            memory_id='mem123',
            actor_id='user1',
            session_id='sess1',
            k=3
        )
        
        assert len(result) == 1
        assert result[0][0]['role'] == 'user'
        assert result[0][0]['content']['text'] == 'Hello'
