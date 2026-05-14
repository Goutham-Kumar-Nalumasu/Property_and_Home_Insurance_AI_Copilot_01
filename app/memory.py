import json
from pathlib import Path
from typing import Any, Dict

from app.config import settings


DEFAULT_MEMORY = {
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


class MemoryManager:
    def __init__(self, memory_file: Path = settings.MEMORY_FILE):
        self.memory_file = memory_file
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.memory_file.exists():
            self._write_all({})

    def _read_all(self) -> Dict[str, Dict[str, Any]]:
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _write_all(self, data: Dict[str, Dict[str, Any]]) -> None:
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get(self, session_id: str) -> Dict[str, Any]:
        all_memory = self._read_all()
        if session_id not in all_memory:
            all_memory[session_id] = DEFAULT_MEMORY.copy()
            self._write_all(all_memory)
        return all_memory[session_id]

    def update(self, session_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        all_memory = self._read_all()
        current = all_memory.get(session_id, DEFAULT_MEMORY.copy())

        for key, value in updates.items():
            if key in DEFAULT_MEMORY and value not in [None, ""]:
                current[key] = value

        all_memory[session_id] = current
        self._write_all(all_memory)
        return current

    def clear(self, session_id: str) -> Dict[str, Any]:
        all_memory = self._read_all()
        all_memory[session_id] = DEFAULT_MEMORY.copy()
        self._write_all(all_memory)
        return all_memory[session_id]


memory_manager = MemoryManager()