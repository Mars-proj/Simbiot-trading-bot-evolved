import time
from typing import Dict
from trading_bot.logging_setup import setup_logging

logger = setup_logging('api_rate_limiter')

class APIRateLimiter:
    def __init__(self, market_state: dict, rate_limit: int, time_window: int):
        self.volatility = market_state['volatility']
        self.rate_limit = rate_limit  # Maximum requests per time window
        self.time_window = time_window  # Time window in seconds
        self.requests: Dict[str, list] = {}

    def can_make_request(self, api_key: str) -> bool:
        """Check if a request can be made within the rate limit."""
        try:
            current_time = time.time()
            if api_key not in self.requests:
                self.requests[api_key] = []
            
            # Remove requests older than the time window
            self.requests[api_key] = [t for t in self.requests[api_key] if current_time - t < self.time_window]
            
            # Check if we can make a new request
            if len(self.requests[api_key]) < self.rate_limit:
                self.requests[api_key].append(current_time)
                logger.info(f"Request allowed for API key {api_key}")
                return True
            
            logger.warning(f"Request denied for API key {api_key} due to rate limit")
            return False
        except Exception as e:
            logger.error(f"Failed to check rate limit for API key {api_key}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    rate_limiter = APIRateLimiter(market_state, rate_limit=5, time_window=60)
    api_key = "test_api_key"
    for _ in range(7):
        if rate_limiter.can_make_request(api_key):
            print("Request allowed")
        else:
            print("Request denied")
        time.sleep(1)
