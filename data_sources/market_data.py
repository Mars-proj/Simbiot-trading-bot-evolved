import asyncio
from trading_bot.logging_setup import setup_logging
from .binance_api import BinanceAPI
from .kraken_api import KrakenAPI
from .mexc_api import MEXCAPI

logger = setup_logging('market_data')

class MarketData:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.exchanges = {
            'binance': BinanceAPI(market_state),
            'kraken': KrakenAPI(market_state),
            'mexc': MEXCAPI(market_state)
        }

    async def get_klines(self, symbol: str, timeframe: str, limit: int, exchange_name: str = 'binance') -> list:
        """Fetch klines data from the specified exchange asynchronously."""
        try:
            if exchange_name not in self.exchanges:
                logger.error(f"Unsupported exchange: {exchange_name}")
                raise ValueError(f"Unsupported exchange: {exchange_name}")
            
            klines = await self.exchanges[exchange_name].get_klines(symbol, timeframe, limit)
            return klines
        except Exception as e:
            logger.error(f"Failed to fetch klines for {symbol} from {exchange_name}: {str(e)}")
            raise

    async def get_symbols(self, exchange_name: str = 'binance') -> list:
        """Fetch available trading symbols from the specified exchange asynchronously."""
        try:
            if exchange_name not in self.exchanges:
                logger.error(f"Unsupported exchange: {exchange_name}")
                raise ValueError(f"Unsupported exchange: {exchange_name}")
            
            symbols = await self.exchanges[exchange_name].get_symbols()
            return symbols
        except Exception as e:
            logger.error(f"Failed to fetch symbols from {exchange_name}: {str(e)}")
            raise
