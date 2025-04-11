import requests
from trading_bot.logging_setup import setup_logging
from trading_bot.utils.api_rate_limiter import APIRateLimiter
from trading_bot.utils.api_utils import APIUtils

logger = setup_logging('mexc_api')

class MEXCAPI:
    def __init__(self, api_key: str, api_secret: str, market_state: dict):
        self.base_url = "https://api.mexc.com"
        self.api_key = api_key
        self.api_secret = api_secret
        self.rate_limiter = APIRateLimiter("mexc", market_state)

    def get_kline(self, symbol: str, interval: str, limit: int = 500):
        """Fetch kline data from MEXC."""
        try:
            self.rate_limiter.limit()
            endpoint = f"{self.base_url}/api/v3/klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            headers = {"X-MEXC-APIKEY": self.api_key}
            
            def request():
                return requests.get(endpoint, params=params, headers=headers)
            
            response = APIUtils.retry_request(request, market_state={'volatility': self.rate_limiter.volatility})
            logger.info(f"Fetched kline data for {symbol} from MEXC")
            return response
        except Exception as e:
            logger.error(f"Failed to fetch kline data from MEXC for {symbol}: {str(e)}")
            raise

    def get_order_book(self, symbol: str, limit: int = 100):
        """Fetch order book from MEXC."""
        try:
            self.rate_limiter.limit()
            endpoint = f"{self.base_url}/api/v3/depth"
            params = {
                "symbol": symbol,
                "limit": limit
            }
            headers = {"X-MEXC-APIKEY": self.api_key}
            
            def request():
                return requests.get(endpoint, params=params, headers=headers)
            
            response = APIUtils.retry_request(request, market_state={'volatility': self.rate_limiter.volatility})
            logger.info(f"Fetched order book for {symbol} from MEXC")
            return response
        except Exception as e:
            logger.error(f"Failed to fetch order book from MEXC for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    api = MEXCAPI("your_api_key", "your_api_secret", market_state)
    kline = api.get_kline("BTCUSDT", "1h")
    print(f"Kline: {kline}")
