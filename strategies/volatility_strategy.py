import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import numpy as np
from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('volatility_strategy')

class VolatilityStrategy(Strategy):
    def __init__(self, market_state: dict, market_data=None):
        super().__init__(market_state, market_data=market_data)
        self.window = 20  # Период для расчёта волатильности
        self.threshold = 0.03  # Порог волатильности (3%)

    async def generate_signal(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'mexc') -> str:
        """Generate a trading signal based on volatility."""
        try:
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if len(klines) < self.window:
                logger.warning(f"Not enough data for {symbol} to calculate volatility")
                return "hold"

            close_prices = [kline['close'] for kline in klines]
            close_array = np.array(close_prices[-self.window:])

            # Рассчитываем волатильность
            returns = np.diff(close_array) / close_array[:-1]
            volatility = np.std(returns)

            # Генерируем сигнал
            if volatility > self.threshold:
                signal = "sell"  # Высокая волатильность — возможен разворот
            else:
                signal = "buy"  # Низкая волатильность — тренд

            logger.info(f"Generated signal for {symbol}: {signal} (Volatility: {volatility})")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate signal for {symbol}: {str(e)}")
            return "hold"
