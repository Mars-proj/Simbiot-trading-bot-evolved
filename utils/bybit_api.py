import requests
from trading_bot.logging_setup import setup_logging
from trading_bot.utils.api_rate_limiter import APIRateLimiter
from trading_bot.utils.api_utils import APIUtils

logger = setup_logging('bybit_api')

class BybitAPI:
    def __init__(self, api_key: str, api_secret: str, market_state: dict):
        self.base_url = "https://api.bybit.com"
        self.api_key = api_key
        self.api_secret = api_secret
        self.rate_limiter = APIRateLimiter("bybit", market_state)

    def get_kline(self, symbol: str, interval: str, limit: int = 200):
        """Fetch kline data from Bybit."""
        try:
            self.rate_limiter.limit()
            endpoint = f"{self.base_url}/v2/public/kline/list"
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            headers = {"api_key": self.api_key}
            
            def request():
                return requests.get(endpoint, params=params, headers=headers)
            
            response = APIUtils.retry_request(request, market_state={'volatility': self.rate_limiter.volatility})
            logger.info(f"Fetched kline data for {symbol} from Bybit")
            return response
        except Exception as e:
            logger.error(f"Failed to fetch kline data from Bybit for {symbol}: {str(e)}")
            raise

    def get_order_book(self, symbol: str):
        """Fetch order book from Bybit."""
        try:
            self.rate_limiter.limit()
            endpoint = f"{self.base_url}/v2/public/orderBook/L2"
            params = {
                "symbol": symbol
            }
            headers = {"api_key": self.api_key}
            
            def request():
                return requests.get(endpoint, params=params, headers=headers)
            
            response = APIUtils.retry_request(request, market_state={'volatility': self.rate_limiter.volatility})
            logger.info(f"Fetched order book for {symbol} from Bybit")
            return response
        except Exception as e:
            logger.error(f"Failed to fetch order book from Bybit for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    api = BybitAPI("your_api_key", "your_api_secret", market_state)
    kline = api.get_kline("BTCUSD", "60")
    print(f"Kline: {kline}")
