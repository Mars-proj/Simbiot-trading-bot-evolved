import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import numpy as np
from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('scalping_strategy')

class ScalpingStrategy(Strategy):
    def __init__(self, market_state: dict, market_data=None):
        super().__init__(market_state, market_data=market_data)
        self.window = 5  # Короткий период для скальпинга
        self.threshold = 0.01  # Порог изменения цены (1%)

    async def generate_signal(self, symbol: str, timeframe: str = '1m', limit: int = 10, exchange_name: str = 'mexc') -> str:
        """Generate a trading signal for scalping."""
        try:
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if len(klines) < self.window:
                logger.warning(f"Not enough data for {symbol} to calculate scalping signal")
                return "hold"

            close_prices = [kline['close'] for kline in klines]
            close_array = np.array(close_prices[-self.window:])

            # Рассчитываем процентное изменение цены
            price_change = (close_array[-1] - close_array[0]) / close_array[0] if close_array[0] != 0 else 0

            # Генерируем сигнал
            if price_change > self.threshold:
                signal = "sell"
            elif price_change < -self.threshold:
                signal = "buy"
            else:
                signal = "hold"

            logger.info(f"Generated signal for {symbol}: {signal} (Price Change: {price_change})")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate signal for {symbol}: {str(e)}")
            return "hold"
