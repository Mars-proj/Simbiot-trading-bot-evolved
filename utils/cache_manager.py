import time
from typing import Any
from trading_bot.logging_setup import setup_logging
import redis
import json

logger = setup_logging('cache_manager')

class CacheManager:
    def __init__(self, market_state: dict, ttl: int = 300):
        self.volatility = market_state['volatility']
        self.ttl = ttl  # Time to live in seconds
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)

    def set(self, key: str, value: Any) -> None:
        """Set a value in the Redis cache with a TTL."""
        try:
            # Сериализуем значение в JSON
            serialized_value = json.dumps(value)
            self.redis_client.setex(key, self.ttl, serialized_value)
            logger.info(f"Set cache value for key {key}")
        except Exception as e:
            logger.error(f"Failed to set cache value for key {key}: {str(e)}")
            raise

    def get(self, key: str) -> Any:
        """Get a value from the Redis cache."""
        try:
            value = self.redis_client.get(key)
            if value:
                # Десериализуем значение из JSON
                deserialized_value = json.loads(value)
                logger.info(f"Retrieved cache value for key {key}")
                return deserialized_value
            logger.info(f"No cache entry found for key {key}")
            return None
        except Exception as e:
            logger.error(f"Failed to get cache value for key {key}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    cache = CacheManager(market_state)
    cache.set("test_key", "test_value")
    value = cache.get("test_key")
    print(f"Cached value: {value}")
