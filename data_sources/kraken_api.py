import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import aiohttp
from utils.logging_setup import setup_logging
from dotenv import load_dotenv

logger = setup_logging('kraken_api')

class KrakenAPI:
    def __init__(self, market_state: dict = None):
        self.market_state = market_state
        load_dotenv()
        self.api_key = os.getenv('KRAKEN_API_KEY')
        self.api_secret = os.getenv('KRAKEN_API_SECRET')
        if not self.api_key or not self.api_secret:
            logger.error("Kraken API keys not found in .env file")
            raise ValueError("Kraken API keys not found")
        self.base_url = "https://api.kraken.com"

    async def get_symbols(self) -> list:
        """Fetch all trading symbols from Kraken."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/0/public/AssetPairs") as response:
                    data = await response.json()
                    symbols = [pair for pair in data['result'].keys()]
                    logger.info(f"Fetched {len(symbols)} symbols from Kraken")
                    return symbols
        except Exception as e:
            logger.error(f"Failed to fetch symbols from Kraken: {str(e)}")
            return []

    async def get_klines(self, symbol: str, timeframe: str, limit: int) -> list:
        """Fetch historical klines for a symbol."""
        try:
            params = {
                'pair': symbol,
                'interval': timeframe,
                'since': 0
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/0/public/OHLC", params=params) as response:
                    data = await response.json()
                    klines = [
                        {
                            'timestamp': int(kline[0]),
                            'open': float(kline[1]),
                            'high': float(kline[2]),
                            'low': float(kline[3]),
                            'close': float(kline[4]),
                            'volume': float(kline[5])
                        }
                        for kline in data['result'][symbol]
                    ]
                    logger.info(f"Fetched {len(klines)} klines for {symbol} from Kraken")
                    return klines[:limit]
        except Exception as e:
            logger.error(f"Failed to fetch klines for {symbol}: {str(e)}")
            return []
