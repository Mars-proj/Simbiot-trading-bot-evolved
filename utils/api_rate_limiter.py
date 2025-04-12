import time
import asyncio
from .logging_setup import setup_logging

logger = setup_logging('api_rate_limiter')

class APIRateLimiter:
    def __init__(self, market_state: dict, requests_per_second: int = 5):
        self.volatility = market_state['volatility']
        self.requests_per_second = requests_per_second
        self.last_request_time = 0

    async def limit(self) -> None:
        """Enforce API rate limiting."""
        try:
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            if time_since_last_request < (1 / self.requests_per_second):
                sleep_time = (1 / self.requests_per_second) - time_since_last_request
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)
            self.last_request_time = time.time()
        except Exception as e:
            logger.error(f"Failed to enforce rate limit: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    limiter = APIRateLimiter(market_state)
    
    async def main():
        for _ in range(10):
            await limiter.limit()
            print("Request made")

    asyncio.run(main())
