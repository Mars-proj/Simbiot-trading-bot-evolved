import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from utils.logging_setup import setup_logging
from .binance_api import BinanceAPI
from .kraken_api import KrakenAPI
from .mexc_api import MexcAPI
from .bitstamp_api import BitstampAPI
from .bybit_api import BybitAPI
from .coinbase_api import CoinbaseAPI
from .huobi_api import HuobiAPI
from .kucoin_api import KucoinAPI
from .roboforex_api import RoboForexAPI

logger = setup_logging('market_data')

class MarketData:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.exchanges = {}
        self._initialize_exchanges()

    def _initialize_exchanges(self):
        """Initialize all supported exchanges."""
        exchange_classes = {
            'binance': BinanceAPI,
            'kraken': KrakenAPI,
            'mexc': MexcAPI,
            'bitstamp': BitstampAPI,
            'bybit': BybitAPI,
            'coinbase': CoinbaseAPI,
            'huobi': HuobiAPI,
            'kucoin': KucoinAPI,
            'roboforex': RoboForexAPI
        }
        for exchange_name, exchange_class in exchange_classes.items():
            try:
                self.exchanges[exchange_name] = exchange_class()
                logger.info(f"Successfully initialized {exchange_name}")
            except Exception as e:
                logger.warning(f"Skipping {exchange_name} due to initialization error: {str(e)}")
                continue

    def get_available_exchanges(self) -> list:
        """Return a list of initialized exchanges."""
        return list(self.exchanges.keys())

    async def get_symbols(self, exchange_name: str) -> list:
        """Get all trading symbols from an exchange."""
        if exchange_name not in self.exchanges:
            logger.error(f"Exchange {exchange_name} not initialized")
            return []
        try:
            return await self.exchanges[exchange_name].get_symbols()
        except Exception as e:
            logger.error(f"Failed to fetch symbols from {exchange_name}: {str(e)}")
            return []

    async def get_klines(self, symbol: str, timeframe: str, limit: int, exchange_name: str) -> list:
        """Get historical klines for a symbol from an exchange."""
        if exchange_name not in self.exchanges:
            logger.error(f"Exchange {exchange_name} not initialized")
            return []
        try:
            return await self.exchanges[exchange_name].get_klines(symbol, timeframe, limit)
        except Exception as e:
            logger.error(f"Failed to fetch klines for {symbol} from {exchange_name}: {str(e)}")
            return []
