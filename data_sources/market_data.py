import asyncio
import ccxt.async_support as ccxt
from utils.logging_setup import setup_logging

logger = setup_logging('market_data')

class AsyncMarketData:
    def __init__(self):
        self.exchanges = {}
        self.logger = setup_logging('market_data')

    async def initialize_exchange(self, exchange_name):
        """Initialize an exchange asynchronously."""
        try:
            if exchange_name not in self.exchanges:
                exchange_class = getattr(ccxt, exchange_name)
                self.exchanges[exchange_name] = exchange_class({
                    'enableRateLimit': True,
                })
            self.logger.info(f"Successfully initialized {exchange_name} (async)")
        except Exception as e:
            self.logger.error(f"Failed to initialize {exchange_name} (async): {str(e)}")
            raise

    async def get_klines(self, symbol, timeframe, limit, exchange_name):
        """Fetch klines asynchronously."""
        try:
            if exchange_name not in self.exchanges:
                await self.initialize_exchange(exchange_name)
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
            self.logger.info("All exchanges cleared")
        except Exception as e:
            self.logger.error(f"Failed to close exchanges: {str(e)}")
