import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import numpy as np
from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('rsi_strategy')

class RSIStrategy(Strategy):
    def __init__(self, market_state: dict, market_data=None):
        super().__init__(market_state, market_data=market_data)
        self.period = 14  # Период для расчёта RSI
        self.overbought = 70  # Порог перекупленности
        self.oversold = 30   # Порог перепроданности

    async def generate_signal(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'mexc') -> str:
        """Generate a trading signal using RSI."""
        try:
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if len(klines) < self.period + 1:
                logger.warning(f"Not enough data for {symbol} to calculate RSI")
                return "hold"

            close_prices = [kline['close'] for kline in klines]
            close_array = np.array(close_prices)

            # Рассчитываем RSI
            deltas = np.diff(close_array)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)

            avg_gain = np.mean(gains[:self.period])
            avg_loss = np.mean(losses[:self.period])
            
            if avg_loss == 0:
                rs = 100
            else:
                rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

            # Корректируем пороги на основе волатильности
            adjusted_overbought = self.overbought + self.volatility * 10
            adjusted_oversold = self.oversold - self.volatility * 10

            # Генерируем сигнал
            if rsi > adjusted_overbought:
                signal = "sell"
            elif rsi < adjusted_oversold:
                signal = "buy"
            else:
                signal = "hold"

            logger.info(f"Generated signal for {symbol}: {signal} (RSI: {rsi}, Overbought: {adjusted_overbought}, Oversold: {adjusted_oversold})")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate signal for {symbol}: {str(e)}")
            return "hold"
