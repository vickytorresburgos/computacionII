import redis.asyncio as redis
import json
from urllib.parse import urlparse
from typing import Any, Dict

DEFAULT_TTL = 300  
DEFAULT_RATE_LIMIT = 10 

class CacheManager:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self._client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    async def get_cached(self, url: str) -> Dict[str, Any] | None:
        """Devuelve el resultado cacheado de una URL si existe."""
        key = f"cache:{url}"
        data = await self._client.get(key)
        return json.loads(data) if data else None

    async def set_cache(self, url: str, data: Dict[str, Any], ttl: int = DEFAULT_TTL) -> None:
        """Guarda un resultado en cache con TTL """
        key = f"cache:{url}"
        await self._client.setex(key, ttl, json.dumps(data))

    async def is_rate_limited(self, url: str, limit: int = DEFAULT_RATE_LIMIT) -> bool:
        """
        Aplica rate limiting por dominio. 
        Devuelve True si el dominio excedió el límite por minuto.
        """
        domain = urlparse(url).netloc or "unknown"
        key = f"ratelimit:{domain}"

        pipe = self._client.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)  
        count, _ = await pipe.execute()

        return int(count) > limit

    async def close(self):
        await self._client.close()