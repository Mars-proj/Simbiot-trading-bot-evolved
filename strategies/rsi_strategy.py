import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('rsi_strategy')

class RSIStrategy(Strategy):
    def __init__(self, market_state, market_data, volatility_analyzer):
        super().__init__(market_state, market_data, volatility_analyzer)
        self.min_order_value = 10.50  # $10 + 5% (hard threshold)

    async def generate_signal(self, symbol: str, timeframe: str, limit: int, exchange_name: str, klines=None):
        """Generate an RSI signal."""
        try:
            if klines is None:
                klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines or len(klines) < 14:
                logger.warning(f"Insufficient klines data for {symbol}")
                return None

            prices = np.array([kline[4] for kline in klines])  # Closing prices
            volatility = self.volatility_analyzer.get_volatility(symbol, timeframe, limit, exchange_name)

            # Calculate RSI
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            avg_gain = np.mean(gains[-14:])
            avg_loss = np.mean(losses[-14:])
            rs = avg_gain / avg_loss if avg_loss != 0 else 0
            rsi = 100 - (100 / (1 + rs))

            # Dynamic thresholds based on volatility
            overbought = 70 - (volatility * 10)  # Decrease overbought threshold with higher volatility
            oversold = 30 + (volatility * 10)    # Increase oversold threshold with higher volatility
            adx_threshold = 20 + (volatility * 10)

            # Calculate ADX (simplified)
            adx = np.mean(np.abs(deltas[-14:])) / np.mean(prices[-14:]) * 100

            # Generate signal
            if rsi > overbought and adx > adx_threshold:
                signal_type = 'sell'
            elif rsi < oversold and adx > adx_threshold:
                signal_type = 'buy'
            else:
                logger.info(f"No RSI signal for {symbol}, RSI={rsi}, ADX={adx}")
                return None

            # Calculate trade size based on volatility
            trade_size = (volatility * 50) / prices[-1]
            if trade_size * prices[-1] < self.min_order_value:
                logger.warning(f"Trade size {trade_size} for {symbol} below minimum order value {self.min_order_value}")
                return None

            signal = {
                'symbol': symbol,
                'strategy': 'rsi',
                'signal': signal_type,
                'entry_price': prices[-1],
                'trade_size': trade_size,
                'timeframe': timeframe,
                'limit': limit,
                'exchange_name': exchange_name,
                'rsi': rsi,
                'adx': adx,
                'overbought': overbought,
                'oversold': oversold,
                'adx_threshold': adx_threshold
            }
            logger.info(f"Generated RSI signal: {signal}")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate RSI signal for {symbol}: {str(e)}")
            return None
