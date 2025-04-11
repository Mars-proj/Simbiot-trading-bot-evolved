import redis
import pickle
from trading_bot.logging_setup import setup_logging
from trading_bot.utils.config_loader import load_config

logger = setup_logging('cache_manager')

class CacheManager:
    def __init__(self, market_state: dict):
        config = load_config(market_state)
        self.redis = redis.Redis(host=config['redis_host'], port=config['redis_port'], db=config['redis_db'])
        self.volatility = market_state['volatility']
        # Динамический TTL: уменьшаем при высокой волатильности
        self.default_ttl = 300 * (1 - self.volatility / 2)  # e.g., 300 to 150

    def get(self, key):
        """Retrieve data from cache."""
        try:
            data = self.redis.get(key)
            if data:
                logger.info(f"Cache hit for key: {key}")
                return pickle.loads(data)
            logger.debug(f"Cache miss for key: {key}")
            return None
        except Exception as e:
            logger.error(f"Failed to get cache for key {key}: {str(e)}")
            raise

    def set(self, key, value, ttl=None):
        """Set data in cache with a dynamic TTL."""
        try:
            ttl = ttl if ttl is not None else self.default_ttl
            serialized = pickle.dumps(value)
            self.redis.setex(key, int(ttl), serialized)
            logger.info(f"Set cache for key: {key} with TTL: {ttl}")
        except Exception as e:
            logger.error(f"Failed to set cache for key {key}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    cache = CacheManager(market_state)
    cache.set("test_key", {"value": 123})
    result = cache.get("test_key")
    print(f"Retrieved from cache: {result}")
