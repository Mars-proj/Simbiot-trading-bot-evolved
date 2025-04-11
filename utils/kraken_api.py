import requests
from trading_bot.logging_setup import setup_logging
from trading_bot.utils.api_rate_limiter import APIRateLimiter
from trading_bot.utils.api_utils import APIUtils

logger = setup_logging('kraken_api')

class KrakenAPI:
    def __init__(self, api_key: str, api_secret: str, market_state: dict):
        self.base_url = "https://api.kraken.com/0/public"
        self.api_key = api_key
        self.api_secret = api_secret
        self.rate_limiter = APIRateLimiter("kraken", market_state)

    def get_ohlc(self, pair: str, interval: int = 60):
        """Fetch OHLC data from Kraken."""
        try:
            self.rate_limiter.limit()
            endpoint = f"{self.base_url}/OHLC"
            params = {
                "pair": pair,
                "interval": interval
            }
            headers = {"API-Key": self.api_key}
            
            def request():
                return requests.get(endpoint, params=params, headers=headers)
            
            response = APIUtils.retry_request(request, market_state={'volatility': self.rate_limiter.volatility})
            logger.info(f"Fetched OHLC data for {pair} from Kraken")
            return response
        except Exception as e:
            logger.error(f"Failed to fetch OHLC data from Kraken for {pair}: {str(e)}")
            raise

    def get_depth(self, pair: str, count: int = 100):
        """Fetch order book (depth) from Kraken."""
        try:
            self.rate_limiter.limit()
            endpoint = f"{self.base_url}/Depth"
            params = {
                "pair": pair,
                "count": count
            }
            headers = {"API-Key": self.api_key}
            
            def request():
                return requests.get(endpoint, params=params, headers=headers)
            
            response = APIUtils.retry_request(request, market_state={'volatility': self.rate_limiter.volatility})
            logger.info(f"Fetched depth for {pair} from Kraken")
            return response
        except Exception as e:
            logger.error(f"Failed to fetch depth from Kraken for {pair}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    api = KrakenAPI("your_api_key", "your_api_secret", market_state)
    ohlc = api.get_ohlc("XBTUSD")
    print(f"OHLC: {ohlc}")
