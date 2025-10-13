"""
AgentCore Memory Service
Manages user preferences and conversation history
"""

from strands_tools.memory import AgentCoreMemory
from typing import Dict, List, Optional
from datetime import datetime


class MemoryService:
    """Wrapper for AgentCore Memory with travel-specific methods"""
    
    def __init__(self, region: str = "us-west-2", memory_id: Optional[str] = None):
        """
        Initialize memory service
        
        Args:
            region: AWS region
            memory_id: Optional memory ID for existing session
        """
        self.memory = AgentCoreMemory(region=region, memory_id=memory_id)
        self.memory_id = memory_id
    
    def store_user_preferences(self, user_id: str, preferences: Dict):
        """
        Store user travel preferences
        
        Args:
            user_id: User identifier
            preferences: Dict with budget, duration, interests, etc.
        """
        self.memory.store(
            key=f"user_preferences_{user_id}",
            value=preferences,
            metadata={
                "type": "preferences",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def get_user_preferences(self, user_id: str) -> Optional[Dict]:
        """Retrieve user preferences"""
        return self.memory.retrieve(f"user_preferences_{user_id}")
    
    def store_conversation(self, session_id: str, message: str, role: str = "user"):
        """
        Store conversation message
        
        Args:
            session_id: Conversation session ID
            message: Message content
            role: 'user' or 'assistant'
        """
        self.memory.store(
            key=f"conversation_{session_id}_{datetime.now().timestamp()}",
            value={"message": message, "role": role},
            metadata={
                "type": "conversation",
                "session_id": session_id,
                "role": role,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Retrieve recent conversation history"""
        results = self.memory.search(
            query=f"session_id:{session_id}",
            filter={"type": "conversation"},
            limit=limit
        )
        return sorted(results, key=lambda x: x.get("timestamp", ""))
    
    def store_travel_recommendation(self, user_id: str, recommendation: Dict):
        """Store travel recommendation result"""
        self.memory.store(
            key=f"recommendation_{user_id}_{datetime.now().timestamp()}",
            value=recommendation,
            metadata={
                "type": "recommendation",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def get_past_recommendations(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Retrieve past recommendations for user"""
        return self.memory.search(
            query=f"user_id:{user_id}",
            filter={"type": "recommendation"},
            limit=limit
        )
