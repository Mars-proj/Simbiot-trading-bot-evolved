import requests
from trading_bot.logging_setup import setup_logging
from trading_bot.utils.api_rate_limiter import APIRateLimiter
from trading_bot.utils.api_utils import APIUtils

logger = setup_logging('coinbase_api')

class CoinbaseAPI:
    def __init__(self, api_key: str, api_secret: str, market_state: dict):
        self.base_url = "https://api.coinbase.com/v2"
        self.api_key = api_key
        self.api_secret = api_secret
        self.rate_limiter = APIRateLimiter("coinbase", market_state)

    def get_candles(self, symbol: str, granularity: int = 3600):
        """Fetch candle data from Coinbase."""
        try:
            self.rate_limiter.limit()
            endpoint = f"{self.base_url}/products/{symbol}/candles"
            params = {
                "granularity": granularity
            }
            headers = {"CB-ACCESS-KEY": self.api_key}
            
            def request():
                return requests.get(endpoint, params=params, headers=headers)
            
            response = APIUtils.retry_request(request, market_state={'volatility': self.rate_limiter.volatility})
            logger.info(f"Fetched candle data for {symbol} from Coinbase")
            return response
        except Exception as e:
            logger.error(f"Failed to fetch candle data from Coinbase for {symbol}: {str(e)}")
            raise

    def get_order_book(self, symbol: str, level: int = 2):
        """Fetch order book from Coinbase."""
        try:
            self.rate_limiter.limit()
            endpoint = f"{self.base_url}/products/{symbol}/book"
            params = {
                "level": level
            }
            headers = {"CB-ACCESS-KEY": self.api_key}
            
            def request():
                return requests.get(endpoint, params=params, headers=headers)
            
            response = APIUtils.retry_request(request, market_state={'volatility': self.rate_limiter.volatility})
            logger.info(f"Fetched order book for {symbol} from Coinbase")
            return response
        except Exception as e:
            logger.error(f"Failed to fetch order book from Coinbase for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    api = CoinbaseAPI("your_api_key", "your_api_secret", market_state)
    candles = api.get_candles("BTC-USD")
    print(f"Candles: {candles}")
