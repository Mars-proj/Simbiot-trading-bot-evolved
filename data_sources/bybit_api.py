import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import aiohttp
from utils.logging_setup import setup_logging
from dotenv import load_dotenv

logger = setup_logging('bybit_api')

class BybitAPI:
    def __init__(self, market_state: dict = None):
        self.market_state = market_state
        load_dotenv()
        self.api_key = os.getenv('BYBIT_API_KEY')
        self.api_secret = os.getenv('BYBIT_API_SECRET')
        if not self.api_key or not self.api_secret:
            logger.error("Bybit API keys not found in .env file")
            raise ValueError("Bybit API keys not found")
        self.base_url = "https://api.bybit.com"

    async def get_symbols(self) -> list:
        """Fetch all trading symbols from Bybit."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/v2/public/symbols") as response:
                    data = await response.json()
                    symbols = [symbol['name'] for symbol in data['result']]
                    logger.info(f"Fetched {len(symbols)} symbols from Bybit")
                    return symbols
        except Exception as e:
            logger.error(f"Failed to fetch symbols from Bybit: {str(e)}")
            return []

    async def get_klines(self, symbol: str, timeframe: str, limit: int) -> list:
        """Fetch historical klines for a symbol."""
        try:
            params = {
                'symbol': symbol,
                'interval': timeframe,
                'limit': limit,
                'from': 0
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/v2/public/kline/list", params=params) as response:
                    data = await response.json()
                    klines = [
                        {
                            'timestamp': int(kline['start_at']),
                            'open': float(kline['open']),
                            'high': float(kline['high']),
                            'low': float(kline['low']),
                            'close': float(kline['close']),
                            'volume': float(kline['volume'])
                        }
                        for kline in data['result']
                    ]
                    logger.info(f"Fetched {len(klines)} klines for {symbol} from Bybit")
                    return klines
        except Exception as e:
            logger.error(f"Failed to fetch klines for {symbol}: {str(e)}")
            return []
