import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import ccxt.async_support as ccxt_async
from utils.logging_setup import setup_logging
from utils.cache_manager import CacheManager

logger = setup_logging('market_data')

class MarketData:
    def __init__(self):
        self.exchanges = {}
        self.cache = CacheManager()

    async def initialize_exchange(self, exchange_name: str, api_key: str = None, api_secret: str = None):
        """Initialize an exchange."""
        try:
            exchange_class = getattr(ccxt_async, exchange_name)
            exchange = exchange_class({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
            })
            await exchange.load_markets()
            self.exchanges[exchange_name] = exchange
            logger.info(f"Successfully initialized {exchange_name}")
        except Exception as e:
            logger.error(f"Failed to initialize {exchange_name}: {str(e)}")
            raise

    async def get_klines(self, symbol: str, timeframe: str, limit: int, exchange_name: str):
        """Fetch klines (candlestick data) for a symbol with caching."""
        cache_key = f"{exchange_name}:{symbol}:{timeframe}:{limit}"
        cached_klines = self.cache.get(cache_key)
        if cached_klines is not None:
            return cached_klines

        if exchange_name not in self.exchanges:
            logger.error(f"Exchange {exchange_name} not initialized")
            return None

        exchange = self.exchanges[exchange_name]
        try:
            klines = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            self.cache.set(cache_key, klines, ttl=600)  # Cache for 10 minutes
            return klines
        except Exception as e:
            logger.error(f"Failed to fetch klines for {symbol} on {exchange_name}: {str(e)}")
            return None

    async def get_supported_timeframes(self, exchange_name: str, symbol: str = None):
        """Get supported timeframes for an exchange."""
        if exchange_name not in self.exchanges:
            logger.error(f"Exchange {exchange_name} not initialized")
            return None

        exchange = self.exchanges[exchange_name]
        try:
            if hasattr(exchange, 'timeframes'):
                return list(exchange.timeframes.keys())
            return ['1m', '5m', '15m', '1h', '4h', '1d']
        except Exception as e:
            logger.error(f"Failed to fetch supported timeframes for {exchange_name}: {str(e)}")
            return None

    async def close(self):
        """Close all exchange connections."""
        for exchange_name, exchange in self.exchanges.items():
            try:
                await exchange.close()
                logger.info(f"Closed connection for {exchange_name}")
            except Exception as e:
                logger.error(f"Failed to close exchange connection for {exchange_name}: {str(e)}")
        self.exchanges.clear()

class SyncMarketData:
    def __init__(self):
        self.exchanges = {}
        self.cache = CacheManager()

    def initialize_exchange(self, exchange_name: str, api_key: str = None, api_secret: str = None):
        """Initialize an exchange synchronously."""
        try:
            exchange_class = getattr(ccxt_async, exchange_name)
            exchange = exchange_class({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
            })
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            markets = loop.run_until_complete(exchange.load_markets())
            self.exchanges[exchange_name] = exchange
            logger.info(f"Successfully initialized {exchange_name} (sync)")
            if not loop.is_running():
                loop.close()
        except Exception as e:
            logger.error(f"Failed to initialize {exchange_name} (sync): {str(e)}")
            raise

    def get_klines(self, symbol: str, timeframe: str, limit: int, exchange_name: str):
        """Fetch klines (candlestick data) for a symbol with caching synchronously."""
        cache_key = f"{exchange_name}:{symbol}:{timeframe}:{limit}"
        cached_klines = self.cache.get(cache_key)
        if cached_klines is not None:
            return cached_klines

        if exchange_name not in self.exchanges:
            logger.error(f"Exchange {exchange_name} not initialized (sync)")
            return None

        exchange = self.exchanges[exchange_name]
        try:
            logger.info(f"Calling fetch_ohlcv for {symbol} on {exchange_name}, exchange type: {type(exchange)}")
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            klines = loop.run_until_complete(exchange.fetch_ohlcv(symbol, timeframe, limit=limit))
            logger.info(f"fetch_ohlcv result for {symbol} on {exchange_name}: {type(klines)}")
            self.cache.set(cache_key, klines, ttl=600)  # Cache for 10 minutes
            return klines
        except Exception as e:
            logger.error(f"Failed to fetch klines for {symbol} on {exchange_name} (sync): {str(e)}")
            return None
        finally:
            if not loop.is_running():
                loop.close()

    def close(self):
        """Close all exchange connections synchronously."""
        for exchange_name, exchange in self.exchanges.items():
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                result = exchange.close()
                logger.info(f"exchange.close result for {exchange_name}: {type(result)}")
                loop.run_until_complete(result)
                logger.info(f"Closed connection for {exchange_name} (sync)")
                if not loop.is_running():
                    loop.close()
            except Exception as e:
                logger.error(f"Failed to close exchange connection for {exchange_name} (sync): {str(e)}")
        self.exchanges.clear()
