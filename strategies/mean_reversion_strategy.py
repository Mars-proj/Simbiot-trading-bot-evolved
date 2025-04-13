import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import numpy as np
from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('mean_reversion_strategy')

class MeanReversionStrategy(Strategy):
    def __init__(self, market_state: dict, market_data=None):
        super().__init__(market_state, market_data=market_data)
        self.window = 20  # Период для расчёта средней
        self.std_multiplier = 2  # Множитель стандартного отклонения

    async def generate_signal(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'mexc') -> str:
        """Generate a trading signal using mean reversion."""
        try:
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if len(klines) < self.window:
                logger.warning(f"Not enough data for {symbol} to calculate mean reversion")
                return "hold"

            close_prices = [kline['close'] for kline in klines]
            close_array = np.array(close_prices[-self.window:])

            mean = np.mean(close_array)
            std = np.std(close_array)
            upper_bound = mean + self.std_multiplier * std
            lower_bound = mean - self.std_multiplier * std
            current_price = close_prices[-1]

            # Генерируем сигнал
            if current_price > upper_bound:
                signal = "sell"
            elif current_price < lower_bound:
                signal = "buy"
            else:
                signal = "hold"

            logger.info(f"Generated signal for {symbol}: {signal} (Price: {current_price}, Upper: {upper_bound}, Lower: {lower_bound})")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate signal for {symbol}: {str(e)}")
            return "hold"
