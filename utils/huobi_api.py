import requests
from trading_bot.logging_setup import setup_logging
from trading_bot.utils.api_rate_limiter import APIRateLimiter
from trading_bot.utils.api_utils import APIUtils

logger = setup_logging('huobi_api')

class HuobiAPI:
    def __init__(self, api_key: str, api_secret: str, market_state: dict):
        self.base_url = "https://api.huobi.pro"
        self.api_key = api_key
        self.api_secret = api_secret
        self.rate_limiter = APIRateLimiter("huobi", market_state)

    def get_kline(self, symbol: str, period: str, size: int = 300):
        """Fetch kline data from Huobi."""
        try:
            self.rate_limiter.limit()
            endpoint = f"{self.base_url}/market/history/kline"
            params = {
                "symbol": symbol,
                "period": period,
                "size": size
            }
            headers = {"Api-Key": self.api_key}
            
            def request():
                return requests.get(endpoint, params=params, headers=headers)
            
            response = APIUtils.retry_request(request, market_state={'volatility': self.rate_limiter.volatility})
            logger.info(f"Fetched kline data for {symbol} from Huobi")
            return response
        except Exception as e:
            logger.error(f"Failed to fetch kline data from Huobi for {symbol}: {str(e)}")
            raise

    def get_depth(self, symbol: str, type: str = "step0"):
        """Fetch order book (depth) from Huobi."""
        try:
            self.rate_limiter.limit()
            endpoint = f"{self.base_url}/market/depth"
            params = {
                "symbol": symbol,
                "type": type
            }
            headers = {"Api-Key": self.api_key}
            
            def request():
                return requests.get(endpoint, params=params, headers=headers)
            
            response = APIUtils.retry_request(request, market_state={'volatility': self.rate_limiter.volatility})
            logger.info(f"Fetched depth for {symbol} from Huobi")
            return response
        except Exception as e:
            logger.error(f"Failed to fetch depth from Huobi for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    api = HuobiAPI("your_api_key", "your_api_secret", market_state)
    kline = api.get_kline("btcusdt", "1hour")
    print(f"Kline: {kline}")
