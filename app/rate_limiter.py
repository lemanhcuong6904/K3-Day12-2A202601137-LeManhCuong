"""CP3 - Redis sliding-window rate limiting."""

from __future__ import annotations

import time
import uuid

from fastapi import HTTPException, status

WINDOW_SECONDS = 60


class RateLimiter:
    def __init__(self, client, limit_per_minute: int) -> None:
        self.client = client
        self.limit = limit_per_minute

    @staticmethod
    def _key(user_id: str) -> str:
        return f"ratelimit:{user_id}"

    def hit_count(self, user_id: str, now: float | None = None) -> int:
        now = now if now is not None else time.time()
        key = self._key(user_id)
        self.client.zremrangebyscore(key, 0, now - WINDOW_SECONDS)
        return int(self.client.zcard(key))

    def check(self, user_id: str, now: float | None = None) -> None:
        now = now if now is not None else time.time()
        if self.hit_count(user_id, now) >= self.limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="rate limit exceeded",
                headers={"Retry-After": str(WINDOW_SECONDS)},
            )

        key = self._key(user_id)
        self.client.zadd(key, {f"{now}:{uuid.uuid4().hex}": now})
        self.client.expire(key, WINDOW_SECONDS)
