import requests
from trading_bot.logging_setup import setup_logging
from trading_bot.utils.api_rate_limiter import APIRateLimiter
from trading_bot.utils.api_utils import APIUtils

logger = setup_logging('kucoin_api')

class KucoinAPI:
    def __init__(self, api_key: str, api_secret: str, market_state: dict):
        self.base_url = "https://api.kucoin.com"
        self.api_key = api_key
        self.api_secret = api_secret
        self.rate_limiter = APIRateLimiter("kucoin", market_state)

    def get_kline(self, symbol: str, kline_type: str, limit: int = 500):
        """Fetch kline data from Kucoin."""
        try:
            self.rate_limiter.limit()
            endpoint = f"{self.base_url}/api/v1/market/candles"
            params = {
                "symbol": symbol,
                "type": kline_type,
                "limit": limit
            }
            headers = {"KC-API-KEY": self.api_key}
            
            def request():
                return requests.get(endpoint, params=params, headers=headers)
            
            response = APIUtils.retry_request(request, market_state={'volatility': self.rate_limiter.volatility})
            logger.info(f"Fetched kline data for {symbol} from Kucoin")
            return response
        except Exception as e:
            logger.error(f"Failed to fetch kline data from Kucoin for {symbol}: {str(e)}")
            raise

    def get_order_book(self, symbol: str):
        """Fetch order book from Kucoin."""
        try:
            self.rate_limiter.limit()
            endpoint = f"{self.base_url}/api/v1/market/orderbook/level2_20"
            params = {
                "symbol": symbol
            }
            headers = {"KC-API-KEY": self.api_key}
            
            def request():
                return requests.get(endpoint, params=params, headers=headers)
            
            response = APIUtils.retry_request(request, market_state={'volatility': self.rate_limiter.volatility})
            logger.info(f"Fetched order book for {symbol} from Kucoin")
            return response
        except Exception as e:
            logger.error(f"Failed to fetch order book from Kucoin for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    api = KucoinAPI("your_api_key", "your_api_secret", market_state)
    kline = api.get_kline("BTC-USDT", "1hour")
    print(f"Kline: {kline}")
