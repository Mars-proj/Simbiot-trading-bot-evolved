import requests
from trading_bot.logging_setup import setup_logging
from trading_bot.utils.api_rate_limiter import APIRateLimiter
from trading_bot.utils.api_utils import APIUtils

logger = setup_logging('binance_api')

class BinanceAPI:
    def __init__(self, api_key: str, api_secret: str, market_state: dict):
        self.base_url = "https://api.binance.com"
        self.api_key = api_key
        self.api_secret = api_secret
        self.rate_limiter = APIRateLimiter("binance", market_state)

    def get_klines(self, symbol: str, interval: str, limit: int = 500):
        """Fetch klines (candlestick data) from Binance."""
        try:
            self.rate_limiter.limit()
            endpoint = f"{self.base_url}/api/v3/klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            headers = {"X-MBX-APIKEY": self.api_key}
            
            def request():
                return requests.get(endpoint, params=params, headers=headers)
            
            response = APIUtils.retry_request(request, market_state={'volatility': self.rate_limiter.volatility})
            logger.info(f"Fetched klines for {symbol} from Binance")
            return response
        except Exception as e:
            logger.error(f"Failed to fetch klines from Binance for {symbol}: {str(e)}")
            raise

    def get_order_book(self, symbol: str, limit: int = 100):
        """Fetch order book from Binance."""
        try:
            self.rate_limiter.limit()
            endpoint = f"{self.base_url}/api/v3/depth"
            params = {
                "symbol": symbol,
                "limit": limit
            }
            headers = {"X-MBX-APIKEY": self.api_key}
            
            def request():
                return requests.get(endpoint, params=params, headers=headers)
            
            response = APIUtils.retry_request(request, market_state={'volatility': self.rate_limiter.volatility})
            logger.info(f"Fetched order book for {symbol} from Binance")
            return response
        except Exception as e:
            logger.error(f"Failed to fetch order book from Binance for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    api = BinanceAPI("your_api_key", "your_api_secret", market_state)
    klines = api.get_klines("BTCUSDT", "1h")
    print(f"Klines: {klines}")
