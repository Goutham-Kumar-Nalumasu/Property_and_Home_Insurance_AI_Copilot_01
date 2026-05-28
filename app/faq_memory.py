import hashlib
import json
import os
from typing import Optional, Dict, Any

import redis
from dotenv import load_dotenv
from langchain_redis import RedisChatMessageHistory

load_dotenv()


class RedisFAQMemory:
    """
    Redis top-layer FAQ memory.

    Flow:
    1. Normalize user question.
    2. Track question frequency.
    3. If answer is cached and question is frequent, return cached answer.
    4. After LLM answer, cache it once question crosses threshold.
    """

    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.ttl_seconds = int(os.getenv("FAQ_CACHE_TTL_SECONDS", "604800"))
        self.min_hits = int(os.getenv("FAQ_MIN_HITS_TO_CACHE", "3"))

        self.client = redis.Redis.from_url(
            self.redis_url,
            decode_responses=True,
        )

    @staticmethod
    def normalize_question(question: str) -> str:
        return " ".join(question.lower().strip().split())

    @staticmethod
    def hash_question(normalized_question: str) -> str:
        return hashlib.sha256(normalized_question.encode("utf-8")).hexdigest()

    def _keys(self, question: str) -> Dict[str, str]:
        normalized = self.normalize_question(question)
        question_hash = self.hash_question(normalized)

        return {
            "normalized": normalized,
            "hash": question_hash,
            "count_key": f"faq:count:{question_hash}",
            "answer_key": f"faq:answer:{question_hash}",
            "meta_key": f"faq:meta:{question_hash}",
        }

    def increment_question_count(self, question: str) -> int:
        keys = self._keys(question)
        count = self.client.incr(keys["count_key"])
        self.client.expire(keys["count_key"], self.ttl_seconds)
        return int(count)

    def get_cached_answer(self, question: str) -> Optional[str]:
        keys = self._keys(question)
        answer = self.client.get(keys["answer_key"])
        return answer

    def should_cache(self, question: str) -> bool:
        keys = self._keys(question)
        count = int(self.client.get(keys["count_key"]) or 0)
        return count >= self.min_hits

    def cache_answer(
        self,
        question: str,
        answer: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        keys = self._keys(question)

        self.client.setex(keys["answer_key"], self.ttl_seconds, answer)

        meta = {
            "normalized_question": keys["normalized"],
            "question_hash": keys["hash"],
            "metadata": metadata or {},
        }

        self.client.setex(
            keys["meta_key"],
            self.ttl_seconds,
            json.dumps(meta),
        )

    def get_top_questions(self, limit: int = 10):
        pattern = "faq:count:*"
        rows = []

        for key in self.client.scan_iter(pattern):
            count = int(self.client.get(key) or 0)
            question_hash = key.replace("faq:count:", "")
            meta_raw = self.client.get(f"faq:meta:{question_hash}")

            question = question_hash
            if meta_raw:
                try:
                    question = json.loads(meta_raw).get(
                        "normalized_question",
                        question_hash,
                    )
                except Exception:
                    pass

            rows.append(
                {
                    "question": question,
                    "count": count,
                    "hash": question_hash,
                }
            )

        return sorted(rows, key=lambda x: x["count"], reverse=True)[:limit]


faq_memory = RedisFAQMemory()