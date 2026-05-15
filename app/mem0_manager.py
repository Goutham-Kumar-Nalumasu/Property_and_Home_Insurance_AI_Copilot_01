import json
from typing import Any, Dict, Optional
from mem0 import Memory
from app.config import settings

class Mem0Manager:
    def __init__(self):
        # Configure local Qdrant
        config = {
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "host": settings.MEM0_HOST,
                    "port": settings.MEM0_PORT,
                    "collection_name": settings.MEM0_COLLECTION_NAME,
                }
            },
            "embedder": {
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small"
                }
            },
            "llm": {
                "provider": "openai",
                "config": {
                    "model": "gpt-4o-mini",
                    "temperature": 0.2
                }
            }
        }
        self.memory = Memory.from_config(config)

    def _get_user_id(self, session_id: str) -> str:
        # Map session_id to a stable user_id for Mem0
        return f"session_{session_id}"

    def get(self, session_id: str) -> Dict[str, Any]:
        """Retrieve all memories for a session as a flat dict (preferences)."""
        user_id = self._get_user_id(session_id)
        # Mem0 returns a list of memory entries; we flatten into a dict
        memories = self.memory.get_all(user_id=user_id)
        flat = {}
        for mem in memories.get("results", []):
            key = mem.get("metadata", {}).get("key")
            value = mem.get("memory")
            if key and value is not None:
                flat[key] = value
        # Ensure default fields exist
        defaults = {
            "policy_type": None,
            "property_type": None,
            "property_size_category": None,
            "postcode": None,
            "damage_type": None,
            "peril_category": None,
            "claim_id": None,
            "last_user_intent": None,
            "conversation_summary": "",
        }
        defaults.update(flat)
        return defaults

    def update(self, session_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Store or update key-value preferences in Mem0."""
        user_id = self._get_user_id(session_id)
        for key, value in updates.items():
            if value is not None and value != "":
                # Store each preference as a separate memory entry with metadata key
                self.memory.add(
                    memory=str(value),
                    user_id=user_id,
                    metadata={"key": key, "session_id": session_id, "type": "preference"},
                )
        # Return full current memory
        return self.get(session_id)

    def clear(self, session_id: str) -> Dict[str, Any]:
        """Delete all memories for a session."""
        user_id = self._get_user_id(session_id)
        self.memory.delete_all(user_id=user_id)
        return self.get(session_id)  # returns default empty dict

    def add_conversation_turn(self, session_id: str, user_msg: str, assistant_msg: str):
        """Store conversation history as episodic memory."""
        user_id = self._get_user_id(session_id)
        history = f"User: {user_msg}\nAssistant: {assistant_msg}"
        self.memory.add(
            memory=history,
            user_id=user_id,
            metadata={"type": "conversation", "timestamp": None},
        )

# Singleton
mem0_manager = Mem0Manager()