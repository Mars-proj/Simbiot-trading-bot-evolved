import requests
from trading_bot.logging_setup import setup_logging
from trading_bot.utils.api_rate_limiter import APIRateLimiter
from trading_bot.utils.api_utils import APIUtils

logger = setup_logging('social_media_fetcher')

class SocialMediaFetcher:
    def __init__(self, api_key: str, market_state: dict):
        self.base_url = "https://api.twitter.com/2"
        self.api_key = api_key
        self.rate_limiter = APIRateLimiter("twitter", market_state)

    def fetch_tweets(self, query: str, max_results: int = 100):
        """Fetch tweets related to a query."""
        try:
            self.rate_limiter.limit()
            endpoint = f"{self.base_url}/tweets/search/recent"
            params = {
                "query": query,
                "max_results": max_results
            }
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            def request():
                return requests.get(endpoint, params=params, headers=headers)
            
            response = APIUtils.retry_request(request, market_state={'volatility': self.rate_limiter.volatility})
            logger.info(f"Fetched tweets for query: {query}")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch tweets for query {query}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    fetcher = SocialMediaFetcher("your_twitter_bearer_token", market_state)
    tweets = fetcher.fetch_tweets("bitcoin")
    print(f"Tweets: {tweets}")
