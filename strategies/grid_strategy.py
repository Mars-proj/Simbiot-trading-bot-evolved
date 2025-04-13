import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import numpy as np
from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('grid_strategy')

class GridStrategy(Strategy):
    def __init__(self, market_state: dict, market_data=None):
        super().__init__(market_state, market_data=market_data)
        self.grid_levels = 5  # Количество уровней сетки
        self.grid_spacing = 0.02  # Шаг между уровнями сетки (2%)

    async def generate_signal(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'mexc') -> str:
        """Generate a trading signal using a grid strategy."""
        try:
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No data for {symbol} to generate grid signal")
                return "hold"

            current_price = klines[-1]['close']
            prices = [kline['close'] for kline in klines]
            avg_price = np.mean(prices)

            # Создаём уровни сетки
            grid_levels = []
            for i in range(-self.grid_levels, self.grid_levels + 1):
                level = avg_price * (1 + i * self.grid_spacing)
                grid_levels.append(level)

            # Находим ближайший уровень сетки
            closest_level = min(grid_levels, key=lambda x: abs(x - current_price))

            # Генерируем сигнал
            if current_price > closest_level:
                signal = "sell"
            else:
                signal = "buy"

            logger.info(f"Generated signal for {symbol}: {signal} (Price: {current_price}, Closest Level: {closest_level})")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate signal for {symbol}: {str(e)}")
            return "hold"
