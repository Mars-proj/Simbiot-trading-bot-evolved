import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('bollinger_strategy')

class BollingerStrategy(Strategy):
    def __init__(self, market_state: dict, market_data):
        super().__init__(market_state, market_data)
        self.base_period = 20
        self.base_deviation = 2

    def calculate_atr(self, klines: list, period: int = 14) -> float:
        """Calculate Average True Range (ATR) for the given klines."""
        if len(klines) < period:
            return 0.0

        tr_values = []
        for i in range(1, len(klines)):
            high = klines[i]['high']
            low = klines[i]['low']
            prev_close = klines[i-1]['close']
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            tr_values.append(tr)

        if not tr_values:
            return 0.0

        atr = np.mean(tr_values[-period:])
        return atr

    async def generate_signal(self, symbol: str, timeframe: str, limit: int, exchange_name: str, predictions=None, volatility=None) -> str:
        """Generate a trading signal using adaptive Bollinger Bands and ATR filter."""
        try:
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No klines data for {symbol}, returning hold signal")
                return 'hold'

            closes = np.array([kline['close'] for kline in klines])
            if len(closes) < self.base_period:
                logger.warning(f"Not enough data for {symbol}, returning hold signal")
                return 'hold'

            # Адаптируем параметры на основе волатильности
            period = self.base_period
            deviation = self.base_deviation
            if volatility is not None:
                # Увеличиваем период и отклонение при высокой волатильности
                period = int(self.base_period * (1 + volatility))
                deviation = self.base_deviation * (1 + volatility)
                logger.info(f"Adjusted Bollinger parameters for {symbol}: period={period}, deviation={deviation}")

            # Рассчитываем Bollinger Bands
            sma = np.mean(closes[-period:])
            std = np.std(closes[-period:])
            upper_band = sma + deviation * std
            lower_band = sma - deviation * std
            current_price = closes[-1]

            # Рассчитываем ATR для фильтрации ложных сигналов
            atr = self.calculate_atr(klines[-period:], period=14)
            atr_threshold = atr * 1.5  # Порог для фильтрации

            # Генерируем сигнал с фильтром ATR
            signal = 'hold'
            if current_price > upper_band and (current_price - sma) > atr_threshold:
                signal = 'sell'
            elif current_price < lower_band and (sma - current_price) > atr_threshold:
                signal = 'buy'

            logger.info(f"Bollinger signal for {symbol}: {signal}, upper={upper_band}, lower={lower_band}, ATR={atr}")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate Bollinger signal for {symbol}: {str(e)}")
            return 'hold'
