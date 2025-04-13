import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('rsi_strategy')

class RSIStrategy(Strategy):
    def __init__(self, market_state: dict, market_data):
        super().__init__(market_state, market_data)
        self.base_period = 14
        self.overbought = 70
        self.oversold = 30

    def calculate_rsi(self, closes: np.ndarray, period: int) -> float:
        """Calculate RSI for the given closes."""
        if len(closes) < period + 1:
            return 50.0

        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])

        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            if avg_loss == 0:
                rsi = 100.0 if avg_gain > 0 else 50.0
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))

        return rsi

    def calculate_adx(self, klines: list, period: int = 14) -> float:
        """Calculate ADX (Average Directional Index) for the given klines."""
        if len(klines) < period + 1:
            return 0.0

        tr_values = []
        plus_dm = []
        minus_dm = []

        for i in range(1, len(klines)):
            high = klines[i]['high']
            low = klines[i]['low']
            prev_high = klines[i-1]['high']
            prev_low = klines[i-1]['low']
            prev_close = klines[i-1]['close']

            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            tr_values.append(tr)

            up_move = high - prev_high
            down_move = prev_low - low
            plus = up_move if up_move > down_move and up_move > 0 else 0
            minus = down_move if down_move > up_move and down_move > 0 else 0
            plus_dm.append(plus)
            minus_dm.append(minus)

        if len(tr_values) < period:
            return 0.0

        atr = np.mean(tr_values[:period])
        plus_di = 100 * np.mean(plus_dm[:period]) / atr if atr != 0 else 0
        minus_di = 100 * np.mean(minus_dm[:period]) / atr if atr != 0 else 0
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di) if (plus_di + minus_di) != 0 else 0

        adx_values = [dx]
        for i in range(period, len(tr_values)):
            atr = (atr * (period - 1) + tr_values[i]) / period
            plus_di = 100 * ((plus_di * (period - 1) + plus_dm[i]) / period) / atr if atr != 0 else 0
            minus_di = 100 * ((minus_di * (period - 1) + minus_dm[i]) / period) / atr if atr != 0 else 0
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di) if (plus_di + minus_di) != 0 else 0
            adx_values.append(dx)

        adx = np.mean(adx_values[-period:])
        return adx

    async def generate_signal(self, symbol: str, timeframe: str, limit: int, exchange_name: str, predictions=None, volatility=None) -> str:
        """Generate a trading signal using adaptive RSI with ADX filter."""
        try:
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No klines data for {symbol}, returning hold signal")
                return 'hold'

            closes = np.array([kline['close'] for kline in klines])
            if len(closes) < self.base_period + 1:
                logger.warning(f"Not enough data for {symbol}, returning hold signal")
                return 'hold'

            # Адаптируем период RSI на основе волатильности
            period = self.base_period
            if volatility is not None:
                period = int(self.base_period * (1 - volatility))  # Уменьшаем период при высокой волатильности
                period = max(5, min(20, period))  # Ограничиваем период
                logger.info(f"Adjusted RSI period for {symbol}: {period}")

            # Рассчитываем RSI
            rsi = self.calculate_rsi(closes, period)

            # Рассчитываем ADX для подтверждения тренда
            adx = self.calculate_adx(klines, period=14)
            adx_threshold = 25  # Порог для сильного тренда

            # Генерируем сигнал с фильтром ADX
            signal = 'hold'
            if rsi > self.overbought and adx > adx_threshold:
                signal = 'sell'
            elif rsi < self.oversold and adx > adx_threshold:
                signal = 'buy'

            logger.info(f"RSI signal for {symbol}: {signal}, RSI={rsi}, ADX={adx}")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate RSI signal for {symbol}: {str(e)}")
            return 'hold'
