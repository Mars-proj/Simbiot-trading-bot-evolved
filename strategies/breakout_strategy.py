import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import numpy as np
from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('breakout_strategy')

class BreakoutStrategy(Strategy):
    def __init__(self, market_state: dict, market_data=None):
        super().__init__(market_state, market_data=market_data)
        self.window = 20  # Период для расчёта уровней breakout

    async def generate_signal(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'mexc') -> str:
        """Generate a trading signal using breakout levels."""
        try:
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if len(klines) < self.window:
                logger.warning(f"Not enough data for {symbol} to calculate breakout levels")
                return "hold"

            high_prices = [kline['high'] for kline in klines]
            low_prices = [kline['low'] for kline in klines]
            close_prices = [kline['close'] for kline in klines]

            high_array = np.array(high_prices[-self.window:])
            low_array = np.array(low_prices[-self.window:])
            current_price = close_prices[-1]

            breakout_high = np.max(high_array) * (1 + self.volatility)
            breakout_low = np.min(low_array) * (1 - self.volatility)

            # Генерируем сигнал
            if current_price > breakout_high:
                signal = "buy"
            elif current_price < breakout_low:
                signal = "sell"
            else:
                signal = "hold"

            logger.info(f"Generated signal for {symbol}: {signal} (Price: {current_price}, Breakout High: {breakout_high}, Breakout Low: {breakout_low})")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate signal for {symbol}: {str(e)}")
            return "hold"
