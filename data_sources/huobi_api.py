import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import aiohttp
from utils.logging_setup import setup_logging
from dotenv import load_dotenv

logger = setup_logging('huobi_api')

class HuobiAPI:
    def __init__(self, market_state: dict = None):
        self.market_state = market_state
        load_dotenv()
        self.api_key = os.getenv('HUOBI_API_KEY')
        self.api_secret = os.getenv('HUOBI_API_SECRET')
        if not self.api_key or not self.api_secret:
            logger.error("Huobi API keys not found in .env file")
            raise ValueError("Huobi API keys not found")
        self.base_url = "https://api.huobi.pro"

    async def get_symbols(self) -> list:
        """Fetch all trading symbols from Huobi."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/v1/common/symbols") as response:
                    data = await response.json()
                    symbols = [symbol['symbol'] for symbol in data['data']]
                    logger.info(f"Fetched {len(symbols)} symbols from Huobi")
                    return symbols
        except Exception as e:
            logger.error(f"Failed to fetch symbols from Huobi: {str(e)}")
            return []

    async def get_klines(self, symbol: str, timeframe: str, limit: int) -> list:
        """Fetch historical klines for a symbol."""
        try:
            params = {
                'symbol': symbol,
                'period': timeframe,
                'size': limit
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/market/history/kline", params=params) as response:
                    data = await response.json()
                    klines = [
                        {
                            'timestamp': int(kline['id']),
                            'open': float(kline['open']),
                            'high': float(kline['high']),
                            'low': float(kline['low']),
                            'close': float(kline['close']),
                            'volume': float(kline['vol'])
                        }
                        for kline in data['data']
                    ]
                    logger.info(f"Fetched {len(klines)} klines for {symbol} from Huobi")
                    return klines
        except Exception as e:
            logger.error(f"Failed to fetch klines for {symbol}: {str(e)}")
            return []
