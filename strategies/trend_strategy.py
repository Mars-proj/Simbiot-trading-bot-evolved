import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import numpy as np
from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('trend_strategy')

class TrendStrategy(Strategy):
    def __init__(self, market_state: dict, market_data=None):
        super().__init__(market_state, market_data=market_data)
        self.window = 20  # Период для расчёта скользящей средней

    async def generate_signal(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'mexc') -> str:
        """Generate a trading signal using trend following."""
        try:
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if len(klines) < self.window:
                logger.warning(f"Not enough data for {symbol} to calculate trend")
                return "hold"

            close_prices = [kline['close'] for kline in klines]
            close_array = np.array(close_prices[-self.window:])

            sma = np.mean(close_array)
            current_price = close_prices[-1]

            # Генерируем сигнал
            if current_price > sma:
                signal = "buy"
            elif current_price < sma:
                signal = "sell"
            else:
                signal = "hold"

            logger.info(f"Generated signal for {symbol}: {signal} (Price: {current_price}, SMA: {sma})")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate signal for {symbol}: {str(e)}")
            return "hold"
