from upstash_redis import Redis


class RedisCache:
    """
    Process-wide singleton for Upstash Redis. First call with valid URL and token
    creates the client; later calls reuse the same instance. If early callers omit
    credentials, a later caller with URL and token can still initialize the client.
    """

    _instance = None

    def __new__(cls, url: str = None, token: str = None):
        if cls._instance is None:
            cls._instance = super(RedisCache, cls).__new__(cls)
            cls._instance.client = None
        inst = cls._instance
        if inst.client is None and url and token:
            inst.client = Redis(url=url, token=token)
        return inst

    def ping(self) -> bool:
        if not self.client:
            return False
        try:
            return self.client.ping() in (True, "PONG", b"PONG")
        except Exception:
            return False

    def get(self, key):
        if not self.client:
            return None
        return self.client.get(key)

    def set(self, key, value, ttl=None):
        if not self.client:
            return None
        if ttl:
            return self.client.set(key, value, ex=ttl)
        return self.client.set(key, value)

    def exists(self, key):
        if not self.client:
            return False
        return self.client.exists(key)

    def delete(self, key):
        if not self.client:
            return None
        return self.client.delete(key)

    def delete_pattern(self, pattern):
        if not self.client:
            return None
        keys = self.client.keys(pattern)
        if keys:
            return self.client.delete(*keys)
        return None

    def hgetall(self, key):
        if not self.client:
            return {}
        result = self.client.hgetall(key)
        return result if result else {}

    def hget(self, key, field):
        if not self.client:
            return None
        return self.client.hget(key, field)

    def hmset(self, key, mapping: dict) -> bool:
        if not self.client or not mapping:
            return False
        self.client.hset(key, values={k: str(v) for k, v in mapping.items()})
        return True

    def expire(self, key, seconds: int) -> bool:
        if not self.client:
            return False
        try:
            return bool(self.client.expire(key, seconds))
        except Exception:
            return False
