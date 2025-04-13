import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import aiohttp
from utils.logging_setup import setup_logging
from dotenv import load_dotenv

logger = setup_logging('coinbase_api')

class CoinbaseAPI:
    def __init__(self, market_state: dict = None):
        self.market_state = market_state
        load_dotenv()
        self.api_key = os.getenv('COINBASE_API_KEY')
        self.api_secret = os.getenv('COINBASE_API_SECRET')
        if not self.api_key or not self.api_secret:
            logger.error("Coinbase API keys not found in .env file")
            raise ValueError("Coinbase API keys not found")
        self.base_url = "https://api.coinbase.com"

    async def get_symbols(self) -> list:
        """Fetch all trading symbols from Coinbase."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/v2/exchange-rates") as response:
                    data = await response.json()
                    symbols = list(data['data']['rates'].keys())
                    logger.info(f"Fetched {len(symbols)} symbols from Coinbase")
                    return symbols
        except Exception as e:
            logger.error(f"Failed to fetch symbols from Coinbase: {str(e)}")
            return []

    async def get_klines(self, symbol: str, timeframe: str, limit: int) -> list:
        """Fetch historical klines for a symbol."""
        try:
            params = {
                'granularity': timeframe,
                'limit': limit
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/v2/prices/{symbol}/spot", params=params) as response:
                    data = await response.json()
                    klines = [
                        {
                            'timestamp': int(kline['time']),
                            'open': float(kline['open']),
                            'high': float(kline['high']),
                            'low': float(kline['low']),
                            'close': float(kline['close']),
                            'volume': float(kline['volume'])
                        }
                        for kline in data['data']
                    ]
                    logger.info(f"Fetched {len(klines)} klines for {symbol} from Coinbase")
                    return klines
        except Exception as e:
            logger.error(f"Failed to fetch klines for {symbol}: {str(e)}")
            return []
