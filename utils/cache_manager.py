import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import redis
import json
from utils.logging_setup import setup_logging

logger = setup_logging('cache_manager')

class CacheManager:
    def __init__(self, host='localhost', port=6379, db=0):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.Redis(host=host, port=port, db=db)
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise

    def set(self, key, value, ttl=600):
        """Set a value in Redis with an optional TTL (in seconds)."""
        try:
            value_json = json.dumps(value)
            self.redis_client.setex(key, ttl, value_json)
            logger.info(f"Cached key: {key} with TTL: {ttl} seconds")
        except Exception as e:
            logger.error(f"Failed to set cache for key {key}: {str(e)}")

    def get(self, key):
        """Get a value from Redis by key."""
        try:
            value_json = self.redis_client.get(key)
            if value_json is None:
                logger.warning(f"Cache miss for key: {key}")
                return None
            value = json.loads(value_json)
            logger.info(f"Cache hit for key: {key}")
            return value
        except Exception as e:
            logger.error(f"Failed to get cache for key {key}: {str(e)}")
            return None

    def delete(self, key):
        """Delete a key from Redis."""
        try:
            self.redis_client.delete(key)
            logger.info(f"Deleted key from cache: {key}")
        except Exception as e:
            logger.error(f"Failed to delete key {key}: {str(e)}")
