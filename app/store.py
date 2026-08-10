"""CP4 - Redis-backed conversation history."""

from __future__ import annotations

import json

import redis

from .config import get_settings

HISTORY_MAX_MESSAGES = 20
HISTORY_TTL_SECONDS = 7 * 24 * 3600


def get_redis_client(url: str | None = None):
    url = url or get_settings().redis_url
    if url.startswith("fake://"):
        import fakeredis

        return fakeredis.FakeRedis(decode_responses=True)
    return redis.from_url(url, decode_responses=True)


class ConversationStore:
    """Store per-user conversation history in Redis, outside the app process."""

    def __init__(self, client) -> None:
        self.client = client

    @staticmethod
    def _key(user_id: str) -> str:
        return f"history:{user_id}"

    def ping(self) -> bool:
        try:
            return bool(self.client.ping())
        except Exception:
            return False

    def append(self, user_id: str, role: str, content: str) -> None:
        key = self._key(user_id)
        payload = json.dumps({"role": role, "content": content}, ensure_ascii=False)
        self.client.rpush(key, payload)
        self.client.ltrim(key, -HISTORY_MAX_MESSAGES, -1)
        self.client.expire(key, HISTORY_TTL_SECONDS)

    def get_history(self, user_id: str) -> list[dict]:
        raw_items = self.client.lrange(self._key(user_id), 0, -1)
        return [json.loads(item) for item in raw_items]

    def clear(self, user_id: str) -> None:
        self.client.delete(self._key(user_id))
