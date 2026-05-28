import os
from typing import List, Dict, Any

from dotenv import load_dotenv
from mem0 import Memory

load_dotenv()


def build_mem0_config() -> Dict[str, Any]:
    return {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": os.getenv(
                    "MEM0_COLLECTION",
                    "homeshield_user_memory",
                ),
                "url": os.getenv("QDRANT_URL", "http://localhost:6333"),
                "api_key": os.getenv("QDRANT_API_KEY") or None,
            },
        },
        "llm": {
            "provider": "openai",
            "config": {
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
        },
        "embedder": {
            "provider": "openai",
            "config": {
                "model": os.getenv(
                    "OPENAI_EMBEDDING_MODEL",
                    "text-embedding-3-small",
                ),
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
        },
        "version": "v1.1",
    }


class Mem0MemoryManager:
    def __init__(self):
        self.memory = Memory.from_config(build_mem0_config())

    def add_interaction(
        self,
        user_id: str,
        user_message: str,
        assistant_message: str,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        messages = [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message},
        ]

        self.memory.add(
            messages,
            user_id=user_id,
            metadata=metadata or {},
        )

    def search_user_memory(
    self,
    user_id: str,
    query: str,
    limit: int = 5,
    ) -> List[Dict[str, Any]]:

        """
        Search long-term memory for a user.

        Newer Mem0 versions do not accept user_id as a top-level parameter
        in search(). They require entity filtering through filters.
        """
        results = self.memory.search(
            query=query,
            filters={
                "user_id": user_id,
            },
            limit=limit,
        )

        if isinstance(results, dict):
            return results.get("results", [])

        return results or []


mem0_memory = Mem0MemoryManager()