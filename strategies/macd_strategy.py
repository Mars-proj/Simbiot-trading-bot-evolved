import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('macd_strategy')

class MACDStrategy(Strategy):
    def __init__(self, market_state: dict, market_data):
        super().__init__(market_state, market_data)
        self.base_fast_period = 12
        self.base_slow_period = 26
        self.base_signal_period = 9

    def calculate_macd(self, closes: np.ndarray, fast_period: int, slow_period: int, signal_period: int) -> tuple:
        """Calculate MACD, Signal Line, and Histogram."""
        if len(closes) < slow_period + signal_period:
            return 0.0, 0.0, 0.0

        def ema(data, period):
            alpha = 2 / (period + 1)
            ema_values = [data[0]]
            for i in range(1, len(data)):
                ema_values.append(alpha * data[i] + (1 - alpha) * ema_values[-1])
            return np.array(ema_values)

        ema_fast = ema(closes, fast_period)
        ema_slow = ema(closes, slow_period)
        macd = ema_fast - ema_slow

        signal = ema(macd[-signal_period-1:], signal_period)
        macd_line = macd[-1]
        signal_line = signal[-1]
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    def calculate_cci(self, klines: list, period: int = 20) -> float:
        """Calculate Commodity Channel Index (CCI)."""
        if len(klines) < period:
            return 0.0

        typical_prices = [(kline['high'] + kline['low'] + kline['close']) / 3 for kline in klines[-period:]]
        sma = np.mean(typical_prices)
        mean_deviation = np.mean([abs(tp - sma) for tp in typical_prices])
        if mean_deviation == 0:
            return 0.0

        cci = (typical_prices[-1] - sma) / (0.015 * mean_deviation)
        return cci

    async def generate_signal(self, symbol: str, timeframe: str, limit: int, exchange_name: str, predictions=None, volatility=None) -> str:
        """Generate a trading signal using adaptive MACD with CCI filter."""
        try:
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No klines data for {symbol}, returning hold signal")
                return 'hold'

            closes = np.array([kline['close'] for kline in klines])
            if len(closes) < self.base_slow_period + self.base_signal_period:
                logger.warning(f"Not enough data for {symbol}, returning hold signal")
                return 'hold'

            fast_period = self.base_fast_period
            slow_period = self.base_slow_period
            signal_period = self.base_signal_period
            if volatility is not None:
                fast_period = int(self.base_fast_period * (1 - volatility / 2))
                slow_period = int(self.base_slow_period * (1 - volatility / 2))
                fast_period = max(5, min(20, fast_period))
                slow_period = max(15, min(40, slow_period))
                logger.info(f"Adjusted MACD parameters for {symbol}: fast={fast_period}, slow={slow_period}")

            macd_line, signal_line, histogram = self.calculate_macd(closes, fast_period, slow_period, signal_period)

            cci = self.calculate_cci(klines, period=20)
            cci_threshold = 50  # Понижаем порог с 100 до 50

            signal = 'hold'
            if macd_line > signal_line and histogram > 0 and cci > cci_threshold:
                signal = 'buy'
            elif macd_line < signal_line and histogram < 0 and cci < -cci_threshold:
                signal = 'sell'

            logger.info(f"MACD signal for {symbol}: {signal}, MACD={macd_line}, Signal={signal_line}, CCI={cci}")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate MACD signal for {symbol}: {str(e)}")
            return 'hold'
