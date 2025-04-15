import asyncio
import ccxt.async_support as ccxt
from utils.logging_setup import setup_logging
import os
from asyncio import Semaphore

class AsyncMarketData:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AsyncMarketData, cls).__new__(cls)
            cls._instance.exchanges = {}
            cls._instance.symbol_cache = {}
            cls._instance.logger = setup_logging('market_data')
            cls._instance.semaphore = Semaphore(10)  # Лимит на 10 одновременных запросов
        return cls._instance

    async def initialize_exchange(self, exchange_name):
        """Initialize an exchange asynchronously."""
        try:
            if exchange_name not in self.exchanges:
                exchange_class = getattr(ccxt, exchange_name)
                if exchange_name == "mexc":
                    self.exchanges[exchange_name] = exchange_class({
                        'enableRateLimit': True,
                        'apiKey': os.getenv('MEXC_API_KEY'),
                        'secret': os.getenv('MEXC_API_SECRET'),
                    })
                elif exchange_name == "binance":
                    self.exchanges[exchange_name] = exchange_class({
                        'enableRateLimit': True,
                        'apiKey': os.getenv('BINANCE_API_KEY'),
                        'secret': os.getenv('BINANCE_API_SECRET'),
                    })
                else:
                    self.exchanges[exchange_name] = exchange_class({
                        'enableRateLimit': True,
                    })
                markets = await self.exchanges[exchange_name].load_markets()
                self.symbol_cache[exchange_name] = set(markets.keys())
            self.logger.info(f"Successfully initialized {exchange_name} (async)")
        except Exception as e:
            self.logger.error(f"Failed to initialize {exchange_name} (async): {str(e)}")
            raise

    async def fetch_klines_with_semaphore(self, symbol, timeframe, limit, exchange_name):
        """Fetch klines with semaphore to limit concurrent requests."""
        async with self.semaphore:
            return await self.get_klines(symbol, timeframe, limit, exchange_name)

    async def get_klines(self, symbol, timeframe, limit, exchange_name):
        """Fetch klines asynchronously."""
        try:
            if exchange_name not in self.exchanges:
                await self.initialize_exchange(exchange_name)

            symbol = symbol.split(':')[0]

            if symbol not in self.symbol_cache.get(exchange_name, set()):
                self.logger.warning(f"Symbol {symbol} not found on {exchange_name}, skipping")
                return None

            self.logger.info(f"Calling fetch_ohlcv for {symbol} on {exchange_name}, exchange type: {type(self.exchanges[exchange_name])}")
            klines = await self.exchanges[exchange_name].fetch_ohlcv(symbol, timeframe, limit=limit)
            self.logger.info(f"fetch_ohlcv result for {symbol} on {exchange_name}: {type(klines)}")
            return klines
        except Exception as e:
            self.logger.error(f"Failed to fetch klines for {symbol} on {exchange_name}: {str(e)}")
            return None

    async def close(self):
        """Close all exchange connections asynchronously."""
        try:
            for exchange_name, exchange in self.exchanges.items():
                self.logger.info(f"Closing connection for {exchange_name} (async)")
                await exchange.close()
                self.logger.info(f"Closed connection for {exchange_name} (async)")
            self.exchanges.clear()
            self.symbol_cache.clear()
            self.logger.info("All exchanges cleared")
        except Exception as e:
            self.logger.error(f"Failed to close exchanges: {str(e)}")
