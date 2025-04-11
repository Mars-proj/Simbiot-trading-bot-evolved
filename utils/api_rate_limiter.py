import time
import redis
from trading_bot.logging_setup import setup_logging
from trading_bot.utils.config_loader import load_config

logger = setup_logging('api_rate_limiter')

class APIRateLimiter:
    def __init__(self, exchange_id: str, market_state: dict):
        config = load_config(market_state)
        self.redis = redis.Redis(host=config['redis_host'], port=config['redis_port'], db=config['redis_db'])
        self.exchange_id = exchange_id
        self.volatility = market_state['volatility']
        # Динамическая частота запросов: уменьшаем при высокой волатильности
        self.requests_per_second = config['api_requests_per_second'] * (1 - self.volatility / 2)  # e.g., 10 to 5
        self.window = 1  # 1 second window
        self.active_users = 0  # Для масштабируемости

    def update_user_count(self, active_users: int):
        """Update the number of active users for dynamic rate limiting."""
        self.active_users = active_users
        # Уменьшаем частоту запросов пропорционально числу пользователей
        self.requests_per_second = max(1, self.requests_per_second / (1 + self.active_users / 1000))

    def limit(self):
        """Limit API requests to the specified rate."""
        try:
            key = f"rate_limit:{self.exchange_id}"
            current_time = int(time.time())
            
            # Increment the counter for the current second
            pipe = self.redis.pipeline()
            pipe.incrby(f"{key}:{current_time}", 1)
            pipe.expire(f"{key}:{current_time}", self.window)
            current_count = pipe.execute()[0]

            if current_count > self.requests_per_second:
                logger.warning(f"Rate limit exceeded for {self.exchange_id}: {current_count} requests (users: {self.active_users}, volatility: {self.volatility})")
                time.sleep(self.window / self.requests_per_second)
            else:
                logger.debug(f"API request allowed for {self.exchange_id}: {current_count}/{self.requests_per_second} (users: {self.active_users})")
        except Exception as e:
            logger.error(f"Failed to apply rate limit for {self.exchange_id}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    limiter = APIRateLimiter("test_exchange", market_state)
    limiter.update_user_count(500)  # 500 active users
    for i in range(15):
        limiter.limit()
        print(f"Request {i+1} processed")
