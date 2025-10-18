"""Strands Memory Hook for AgentCore Memory integration"""

from strands.hooks import AgentInitializedEvent, HookProvider, MessageAddedEvent
from tools.memory_tools import create_memory_event, get_conversation_history
from tools.config import ToolConfig


class MemoryHook(HookProvider):
    """AgentCore Memory統合用Hook"""

    def __init__(self, memory_id: str = None, k_turns: int = 3):
        self.memory_id = memory_id or ToolConfig.MEMORY_ID
        self.k_turns = k_turns

    def on_agent_initialized(self, event):
        """load conversation history from memory when agent is initialized"""
        if not self.memory_id:
            return

        session_id = getattr(event.agent.state, "session_id", "default")
        turns = get_conversation_history(
            memory_id=self.memory_id,
            actor_id="user",
            session_id=session_id,
            k=self.k_turns,
        )

        if turns:
            context = "\n".join(
                [f"{m['role']}: {m['content']['text']}" for t in turns for m in t]
            )
            event.agent.system_prompt += f"\n\nPrevious:\n{context}"

    def on_message_added(self, event):
        """save conversation history to memory when message is added"""
        if not self.memory_id:
            return

        msg = event.agent.messages[-1]
        session_id = getattr(event.agent.state, "session_id", "default")

        create_memory_event(
            memory_id=self.memory_id,
            actor_id="user",
            session_id=session_id,
            messages=[(str(msg["content"]), msg["role"])],
        )

    def register_hooks(self, registry):
        """register hooks"""
        registry.add_callback(AgentInitializedEvent, self.on_agent_initialized)
        registry.add_callback(MessageAddedEvent, self.on_message_added)
