import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import numpy as np
from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('macd_strategy')

class MACDStrategy(Strategy):
    def __init__(self, market_state: dict, market_data=None):
        super().__init__(market_state, market_data=market_data)
        self.fast_period = 12  # Быстрый период для MACD
        self.slow_period = 26  # Медленный период для MACD
        self.signal_period = 9  # Период для сигнальной линии

    async def generate_signal(self, symbol: str, timeframe: str = '1h', limit: int = 50, exchange_name: str = 'mexc') -> str:
        """Generate a trading signal using MACD."""
        try:
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if len(klines) < self.slow_period + self.signal_period:
                logger.warning(f"Not enough data for {symbol} to calculate MACD")
                return "hold"

            close_prices = [kline['close'] for kline in klines]
            close_array = np.array(close_prices)

            # Рассчитываем EMA
            def ema(data, period):
                weights = np.exp(np.linspace(-1., 0., period))
                weights /= weights.sum()
                ema = np.convolve(data, weights, mode='valid')
                return np.concatenate([np.full(period - 1, np.nan), ema])

            ema_fast = ema(close_array, self.fast_period)
            ema_slow = ema(close_array, self.slow_period)
            
            # Рассчитываем MACD
            macd = ema_fast[-len(ema_slow):] - ema_slow
            signal_line = ema(macd, self.signal_period)

            # Последние значения
            macd_value = macd[-1]
            signal_value = signal_line[-1]

            # Генерируем сигнал
            if macd_value > signal_value:
                signal = "buy"
            elif macd_value < signal_value:
                signal = "sell"
            else:
                signal = "hold"

            logger.info(f"Generated signal for {symbol}: {signal} (MACD: {macd_value}, Signal: {signal_value})")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate signal for {symbol}: {str(e)}")
            return "hold"
