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
        self.supported_timeframes = {}  # Для хранения поддерживаемых таймфреймов для каждой биржи
        self._initialize_exchanges()

    def _initialize_exchanges(self):
        """Initialize all supported exchanges."""
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
                self.exchanges[exchange_name] = exchange_class()
                logger.info(f"Successfully initialized {exchange_name}")
            except Exception as e:
                logger.warning(f"Skipping {exchange_name} due to initialization error: {str(e)}")
                continue

    def get_available_exchanges(self) -> list:
        """Return a list of initialized exchanges."""
        return list(self.exchanges.keys())

    async def get_supported_timeframes(self, exchange_name: str, symbol: str) -> list:
        """Determine supported timeframes for the exchange by testing with a symbol."""
        if exchange_name not in self.exchanges:
            logger.error(f"Exchange {exchange_name} not initialized")
            return []

        if exchange_name in self.supported_timeframes:
            return self.supported_timeframes[exchange_name]

        # Список возможных таймфреймов для тестирования
        possible_timeframes = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
        supported = []

        for timeframe in possible_timeframes:
            try:
                # Пробуем получить одну свечу для теста
                klines = await self.exchanges[exchange_name].get_klines(symbol, timeframe, 1)
                if klines and isinstance(klines, list) and len(klines) > 0:
                    supported.append(timeframe)
                    logger.info(f"Timeframe {timeframe} is supported on {exchange_name}")
            except Exception as e:
                logger.debug(f"Timeframe {timeframe} not supported on {exchange_name}: {str(e)}")
                continue

        self.supported_timeframes[exchange_name] = supported
        logger.info(f"Supported timeframes for {exchange_name}: {supported}")
        return supported

    async def get_symbols(self, exchange_name: str) -> list:
        """Get all trading symbols from an exchange."""
        if exchange_name not in self.exchanges:
            logger.error(f"Exchange {exchange_name} not initialized")
            return []
        try:
            symbols = await self.exchanges[exchange_name].get_symbols()
            if not symbols:
                logger.warning(f"No symbols available on {exchange_name}. Skipping this exchange.")
                del self.exchanges[exchange_name]  # Удаляем биржу из списка, если символы не получены
            return symbols
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
