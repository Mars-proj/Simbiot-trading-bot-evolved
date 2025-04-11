import requests
from trading_bot.logging_setup import setup_logging
from trading_bot.utils.api_rate_limiter import APIRateLimiter
from trading_bot.utils.api_utils import APIUtils

logger = setup_logging('news_fetcher')

class NewsFetcher:
    def __init__(self, api_key: str, market_state: dict):
        self.base_url = "https://newsapi.org/v2"
        self.api_key = api_key
        self.rate_limiter = APIRateLimiter("newsapi", market_state)

    def fetch_news(self, query: str, language: str = "en", page_size: int = 20):
        """Fetch news articles related to a query."""
        try:
            self.rate_limiter.limit()
            endpoint = f"{self.base_url}/everything"
            params = {
                "q": query,
                "language": language,
                "pageSize": page_size,
                "apiKey": self.api_key
            }
            
            def request():
                return requests.get(endpoint, params=params)
            
            response = APIUtils.retry_request(request, market_state={'volatility': self.rate_limiter.volatility})
            logger.info(f"Fetched news for query: {query}")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch news for query {query}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    fetcher = NewsFetcher("your_newsapi_key", market_state)
    news = fetcher.fetch_news("bitcoin")
    print(f"News: {news}")
