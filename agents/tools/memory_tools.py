"""Memory tools for AgentCore Memory integration"""

from datetime import datetime
import uuid
from typing import Dict, List, Any, Optional
from .base_tool import DataSourceTool
from .config import ToolConfig


class MemoryTool(DataSourceTool):
    """AgentCore Memory操作ツール"""

    def _create_client(self):
        from bedrock_agentcore.memory import MemoryClient

        return MemoryClient(region_name=ToolConfig.AWS_REGION)

    def execute(self, operation: str, **kwargs) -> Any:
        if operation == "create_event":
            return self._create_event(**kwargs)
        elif operation == "get_last_k_turns":
            return self._get_last_k_turns(**kwargs)
        raise ValueError(f"Unknown operation: {operation}")

    def _create_event(
        self,
        memory_id: str,
        actor_id: str,
        session_id: str,
        messages: List[tuple],
        event_timestamp: Optional[datetime] = None,
    ) -> Dict:
        if event_timestamp is None:
            event_timestamp = datetime.utcnow()

        response = self.client.create_event(
            memory_id=memory_id,
            actor_id=actor_id,
            session_id=session_id,
            event_timestamp=event_timestamp,
            messages=messages,
            client_token=str(uuid.uuid4()),
        )
        return response["event"]

    def _get_last_k_turns(
        self, memory_id: str, actor_id: str, session_id: str, k: int = 3
    ) -> List[Dict]:
        return self.client.get_last_k_turns(
            memory_id=memory_id, actor_id=actor_id, session_id=session_id, k=k
        )


_memory_tool = MemoryTool()


def create_memory_event(
    memory_id: str, actor_id: str, session_id: str, messages: List[tuple]
) -> Dict:
    """Memory\u306b\u30a4\u30d9\u30f3\u30c8\u3092\u4fdd\u5b58"""
    return _memory_tool.execute(
        "create_event",
        memory_id=memory_id,
        actor_id=actor_id,
        session_id=session_id,
        messages=messages,
    )


def get_conversation_history(
    memory_id: str, actor_id: str, session_id: str, k: int = 3
) -> List[Dict]:
    """Memory\u304b\u3089\u4f1a\u8a71\u5c65\u6b74\u3092\u53d6\u5f97"""
    return _memory_tool.execute(
        "get_last_k_turns",
        memory_id=memory_id,
        actor_id=actor_id,
        session_id=session_id,
        k=k,
    )
