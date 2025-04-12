import requests
from trading_bot.logging_setup import setup_logging

logger = setup_logging('api_utils')

class APIUtils:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']

    def make_request(self, url: str, params: dict = None) -> dict:
        """Make an API request."""
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Successfully made API request to {url}")
            return data
        except Exception as e:
            logger.error(f"Failed to make API request to {url}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    api_utils = APIUtils(market_state)
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {'symbol': 'BTCUSDT'}
    data = api_utils.make_request(url, params)
    print(f"API response: {data}")

