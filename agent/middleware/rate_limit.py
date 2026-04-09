"""
Django Rate Limiting Middleware for /agent/chat endpoint.

Uses Token Bucket algorithm with Upstash Redis (singleton RedisCache).
Supports both per-user and global rate limits.
"""

import logging
import os
import time
from typing import Optional, Tuple

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from singleton.Redis import RedisCache

logger = logging.getLogger(__name__)


class TokenBucketRateLimiter:
    """
    Token Bucket rate limiter backed by Redis (RedisCache / Upstash).
    """

    def __init__(
        self,
        redis_client: RedisCache,
        bucket_capacity: int,
        refill_interval: int = 60,
    ):
        self.redis = redis_client
        self.capacity = bucket_capacity
        self.interval = refill_interval

    def is_allowed(self, key: str) -> Tuple[bool, int]:
        """Check if request is allowed and consume token."""
        now = int(time.time())

        bucket = self.redis.hgetall(key)

        if not bucket:
            tokens = self.capacity - 1
            self.redis.hmset(
                key,
                {
                    "tokens": str(tokens),
                    "last_refill": str(now),
                },
            )
            self.redis.expire(key, self.interval * 2)
            return True, tokens

        try:
            tokens = int(bucket.get("tokens", 0))
            last_refill = int(bucket.get("last_refill", now))
        except (ValueError, TypeError):
            tokens = 0
            last_refill = now

        elapsed = now - last_refill
        refill_rate = self.capacity / self.interval
        tokens_to_add = int(elapsed * refill_rate)

        if tokens_to_add > 0:
            tokens = min(self.capacity, tokens + tokens_to_add)
            last_refill = now

        if tokens < 1:
            return False, 0

        new_tokens = tokens - 1
        self.redis.hmset(
            key,
            {
                "tokens": str(new_tokens),
                "last_refill": str(last_refill),
            },
        )
        self.redis.expire(key, self.interval * 2)

        return True, new_tokens

    def get_retry_after(self, key: str) -> int:
        """Calculate retry-after time in seconds."""
        bucket = self.redis.hgetall(key)
        if not bucket:
            return 0

        try:
            tokens = int(bucket.get("tokens", 0))
            if tokens > 0:
                return 0

            last_refill = int(bucket.get("last_refill", int(time.time())))
            elapsed = time.time() - last_refill
            refill_rate = self.interval / self.capacity
            return max(1, int(refill_rate - (elapsed % refill_rate)))
        except (ValueError, TypeError):
            return 0


class RateLimitMiddleware(MiddlewareMixin):
    """
    Token Bucket rate limiting middleware for /agent/chat.
    """

    def __init__(self, get_response):
        super().__init__(get_response)

        self.local_limit = int(os.getenv("RATE_LIMIT_LOCAL", "10"))
        self.global_limit = int(os.getenv("RATE_LIMIT_GLOBAL", "20"))
        self.refresh_interval = int(os.getenv("RATE_LIMIT_INTERVAL", "60"))
        self.burst_capacity = int(os.getenv("RATE_LIMIT_BURST", "15"))

        self.local_key_prefix = "ratelimit:local"
        self.global_key_prefix = "ratelimit:global"

        self.redis: Optional[RedisCache] = None
        self.local_limiter: Optional[TokenBucketRateLimiter] = None
        self.global_limiter: Optional[TokenBucketRateLimiter] = None
        self._init_redis()

    def _init_redis(self):
        try:
            redis_url = os.getenv("UPSTASH_REDIS_REST_URL")
            redis_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
            if not redis_url or not redis_token:
                logger.error("Upstash Redis credentials not configured")
                return

            self.redis = RedisCache(url=redis_url, token=redis_token)
            if self.redis.client is None:
                logger.error("Redis singleton has no client (missing URL/token)")
                return

            if not self.redis.ping():
                logger.error("Failed to connect to Upstash Redis (ping failed)")
                self.redis = None
                return

            self.local_limiter = TokenBucketRateLimiter(
                self.redis,
                bucket_capacity=self.burst_capacity or self.local_limit,
                refill_interval=self.refresh_interval,
            )
            self.global_limiter = TokenBucketRateLimiter(
                self.redis,
                bucket_capacity=self.global_limit,
                refill_interval=self.refresh_interval,
            )

            logger.info(
                "Rate limiter initialized - Local: %s req/%ss, Global: %s req/%ss",
                self.local_limit,
                self.refresh_interval,
                self.global_limit,
                self.refresh_interval,
            )

        except Exception as e:
            logger.error("Failed to initialize Upstash Redis: %s", e)
            self.redis = None
            self.local_limiter = None
            self.global_limiter = None

    def _get_client_ip(self, request) -> str:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")

    def _get_user_id(self, request) -> Optional[str]:
        if hasattr(request, "user") and request.user.is_authenticated:
            return f"user_{request.user.id}"
        return None

    def _get_rate_limit_keys(self, request) -> Tuple[str, str]:
        user_id = self._get_user_id(request)
        if user_id:
            local_key = f"{self.local_key_prefix}:{user_id}"
        else:
            ip = self._get_client_ip(request)
            local_key = f"{self.local_key_prefix}:ip:{ip}"

        global_key = f"{self.global_key_prefix}:all"
        return local_key, global_key

    def _check_rate_limits(self, request) -> Optional[Tuple[bool, int, str]]:
        if not self.redis or not self.local_limiter or not self.global_limiter:
            return None

        local_key, global_key = self._get_rate_limit_keys(request)

        global_allowed, _ = self.global_limiter.is_allowed(global_key)
        if not global_allowed:
            retry_after = self.global_limiter.get_retry_after(global_key)
            logger.warning(
                "Global rate limit exceeded - Key: %s, Client: %s",
                global_key,
                self._get_client_ip(request),
            )
            return False, retry_after, "global"

        local_allowed, _ = self.local_limiter.is_allowed(local_key)
        if not local_allowed:
            retry_after = self.local_limiter.get_retry_after(local_key)
            logger.warning(
                "Local rate limit exceeded - Key: %s, User: %s, Client: %s",
                local_key,
                self._get_user_id(request) or "anonymous",
                self._get_client_ip(request),
            )
            return False, retry_after, "local"

        return True, 0, None

    def _is_target_path(self, request) -> bool:
        path = request.path or ""
        normalized = path.rstrip("/") or "/"
        return normalized == "/agent/chat"

    def process_request(self, request):
        if not self._is_target_path(request):
            return None

        if request.method == "OPTIONS":
            return None

        result = self._check_rate_limits(request)
        if result is None:
            return None

        is_allowed, retry_after, limit_type = result

        if not is_allowed:
            response_data = {
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please wait before retrying.",
                "limit_type": limit_type,
                "retry_after": retry_after,
                "limit": self.global_limit if limit_type == "global" else self.local_limit,
                "window": self.refresh_interval,
            }

            response = JsonResponse(
                response_data,
                status=429,
                json_dumps_params={"indent": 2},
            )

            response["Retry-After"] = str(retry_after)
            response["X-RateLimit-Limit"] = str(
                self.global_limit if limit_type == "global" else self.local_limit
            )
            response["X-RateLimit-Reset"] = str(int(time.time()) + retry_after)

            return response

        return None

    def process_response(self, request, response):
        if not self._is_target_path(request):
            return response

        if self.redis and self.local_limiter and response.status_code < 400:
            try:
                local_key, _ = self._get_rate_limit_keys(request)
                tokens_raw = self.redis.hget(local_key, "tokens")
                if tokens_raw is not None:
                    remaining = int(tokens_raw)
                    response["X-RateLimit-Limit"] = str(self.local_limit)
                    response["X-RateLimit-Remaining"] = str(remaining)
                    response["X-RateLimit-Window"] = str(self.refresh_interval)
            except Exception:
                pass

        return response
