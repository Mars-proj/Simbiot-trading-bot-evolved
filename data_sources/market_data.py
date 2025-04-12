import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from utils.logging_setup import setup_logging
from .binance_api import BinanceAPI
from .kraken_api import KrakenAPI
from .mexc_api import MEXCAPI
from .bitstamp_api import BitstampAPI
from .bybit_api import BybitAPI
from .coinbase_api import CoinbaseAPI
from .huobi_api import HuobiAPI
from .kucoin_api import KuCoinAPI

logger = setup_logging('market_data')

class MarketData:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.exchanges = {}
        self.available_exchanges = []

        # Инициализируем биржи, пропуская те, где ключи невалидны
        exchange_classes = {
            'binance': BinanceAPI,
            'kraken': KrakenAPI,
            'mexc': MEXCAPI,
            'bitstamp': BitstampAPI,
            'bybit': BybitAPI,
            'coinbase': CoinbaseAPI,
            'huobi': HuobiAPI,
            'kucoin': KuCoinAPI
        }

        for exchange_name, exchange_class in exchange_classes.items():
            try:
                self.exchanges[exchange_name] = exchange_class(market_state)
                self.available_exchanges.append(exchange_name)
                logger.info(f"Successfully initialized {exchange_name}")
            except Exception as e:
                logger.warning(f"Skipping {exchange_name} due to initialization error: {str(e)}")

        if not self.available_exchanges:
            logger.error("No valid exchanges available")
            raise ValueError("No valid exchanges available")

    async def get_klines(self, symbol: str, timeframe: str, limit: int, exchange_name: str = 'mexc') -> list:
        """Fetch klines data from the specified exchange asynchronously."""
        try:
            if exchange_name not in self.available_exchanges:
                logger.warning(f"Exchange {exchange_name} is not available, skipping")
                return []

            klines = await self.exchanges[exchange_name].get_klines(symbol, timeframe, limit)
            return klines
        except Exception as e:
            logger.error(f"Failed to fetch klines for {symbol} from {exchange_name}: {str(e)}")
            return []

    async def get_symbols(self, exchange_name: str = 'mexc') -> list:
        """Fetch available trading symbols from the specified exchange asynchronously."""
        try:
            if exchange_name not in self.available_exchanges:
                logger.warning(f"Exchange {exchange_name} is not available, skipping")
                return []

            symbols = await self.exchanges[exchange_name].get_symbols()
            return symbols
        except Exception as e:
            logger.error(f"Failed to fetch symbols from {exchange_name}: {str(e)}")
            return []

    def get_available_exchanges(self) -> list:
        """Return the list of available exchanges."""
        return self.available_exchanges
