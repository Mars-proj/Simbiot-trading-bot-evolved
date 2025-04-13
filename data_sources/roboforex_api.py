import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import MetaTrader5 as mt5
from utils.logging_setup import setup_logging

logger = setup_logging('roboforex_api')

class RoboForexAPI:
    def __init__(self):
        if not mt5.initialize():
            logger.error("Failed to initialize MetaTrader5")
            raise ValueError("MetaTrader5 initialization failed")
        logger.info("Successfully initialized RoboForex via MetaTrader5")

    def __del__(self):
        mt5.shutdown()

    async def get_symbols(self) -> list:
        """Fetch all trading symbols from RoboForex."""
        try:
            symbols = mt5.symbols_get()
            active_symbols = [symbol.name for symbol in symbols if symbol.visible]
            logger.info(f"Fetched {len(active_symbols)} symbols from RoboForex")
            return active_symbols
        except Exception as e:
            logger.error(f"Failed to fetch symbols from RoboForex: {str(e)}")
            return []

    async def get_klines(self, symbol: str, timeframe: str, limit: int) -> list:
        """Fetch historical klines for a symbol."""
        try:
            timeframe_map = {
                '1m': mt5.TIMEFRAME_M1,
                '1h': mt5.TIMEFRAME_H1,
                '1d': mt5.TIMEFRAME_D1
            }
            if timeframe not in timeframe_map:
                logger.error(f"Unsupported timeframe: {timeframe}")
                return []
            
            rates = mt5.copy_rates_from_pos(symbol, timeframe_map[timeframe], 0, limit)
            if rates is None or len(rates) == 0:
                logger.warning(f"No klines data for {symbol}")
                return []
            
            klines = [
                {
                    'timestamp': int(rate['time']),
                    'open': float(rate['open']),
                    'high': float(rate['high']),
                    'low': float(rate['low']),
                    'close': float(rate['close']),
                    'volume': int(rate['tick_volume'])
                }
                for rate in rates
            ]
            logger.info(f"Fetched {len(klines)} klines for {symbol} from RoboForex")
            return klines
        except Exception as e:
            logger.error(f"Failed to fetch klines for {symbol}: {str(e)}")
            return []
