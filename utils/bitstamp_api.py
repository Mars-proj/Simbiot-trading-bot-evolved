import requests
from trading_bot.logging_setup import setup_logging
from trading_bot.utils.api_rate_limiter import APIRateLimiter
from trading_bot.utils.api_utils import APIUtils

logger = setup_logging('bitstamp_api')

class BitstampAPI:
    def __init__(self, market_state: dict):
        self.base_url = "https://www.bitstamp.net/api/v2"
        self.rate_limiter = APIRateLimiter("bitstamp", market_state)

    def get_ohlc(self, symbol: str, step: int = 3600, limit: int = 1000):
        """Fetch OHLC data from Bitstamp."""
        try:
            self.rate_limiter.limit()
            endpoint = f"{self.base_url}/ohlc/{symbol}/"
            params = {
                "step": step,
                "limit": limit
            }
            
            def request():
                return requests.get(endpoint, params=params)
            
            response = APIUtils.retry_request(request, market_state={'volatility': self.rate_limiter.volatility})
            logger.info(f"Fetched OHLC data for {symbol} from Bitstamp")
            return response
        except Exception as e:
            logger.error(f"Failed to fetch OHLC data from Bitstamp for {symbol}: {str(e)}")
            raise

    def get_order_book(self, symbol: str):
        """Fetch order book from Bitstamp."""
        try:
            self.rate_limiter.limit()
            endpoint = f"{self.base_url}/order_book/{symbol}/"
            
            def request():
                return requests.get(endpoint)
            
            response = APIUtils.retry_request(request, market_state={'volatility': self.rate_limiter.volatility})
            logger.info(f"Fetched order book for {symbol} from Bitstamp")
            return response
        except Exception as e:
            logger.error(f"Failed to fetch order book from Bitstamp for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    api = BitstampAPI(market_state)
    ohlc = api.get_ohlc("btcusd")
    print(f"OHLC: {ohlc}")
