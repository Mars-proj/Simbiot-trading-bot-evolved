import time
from typing import Any
from trading_bot.logging_setup import setup_logging

logger = setup_logging('cache_manager')

class CacheManager:
    def __init__(self, market_state: dict, ttl: int = 300):
        self.volatility = market_state['volatility']
        self.ttl = ttl  # Time to live in seconds
        self.cache: dict = {}

    def set(self, key: str, value: Any) -> None:
        """Set a value in the cache with a TTL."""
        try:
            expiration = time.time() + self.ttl
            self.cache[key] = (value, expiration)
            logger.info(f"Set cache value for key {key}")
        except Exception as e:
            logger.error(f"Failed to set cache value for key {key}: {str(e)}")
            raise

    def get(self, key: str) -> Any:
        """Get a value from the cache."""
        try:
            if key in self.cache:
                value, expiration = self.cache[key]
                if time.time() < expiration:
                    logger.info(f"Retrieved cache value for key {key}")
                    return value
                else:
                    del self.cache[key]
                    logger.info(f"Cache entry for key {key} expired")
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
