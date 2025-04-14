import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('trend_strategy')

class TrendStrategy(Strategy):
    def __init__(self, market_state, market_data, volatility_analyzer):
        super().__init__(market_state, market_data, volatility_analyzer)
        self.min_order_value = 10.50  # $10 + 5% (hard threshold)

    async def generate_signal(self, symbol: str, timeframe: str, limit: int, exchange_name: str, klines=None):
        """Generate a trend-following signal."""
        try:
            if klines is None:
                klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines or len(klines) < 100:
                logger.warning(f"Insufficient klines data for {symbol}")
                return None

            prices = np.array([kline[4] for kline in klines])  # Closing prices
            volatility = self.volatility_analyzer.get_volatility(symbol, timeframe, limit, exchange_name)

            # Dynamic trend period based on volatility
            trend_period = int(100 * (1 + volatility / 2))
            adx_threshold = 20 + (volatility * 10)

            # Calculate moving average
            ma = np.mean(prices[-trend_period:])
            current_price = prices[-1]

            # Calculate ADX (simplified)
            deltas = np.diff(prices[-14:])
            adx = np.mean(np.abs(deltas)) / np.mean(prices[-14:]) * 100

            # Generate signal
            if current_price > ma and adx > adx_threshold:
                signal_type = 'buy'
            elif current_price < ma and adx > adx_threshold:
                signal_type = 'sell'
            else:
                logger.info(f"No trend signal for {symbol}, price={current_price}, MA={ma}, ADX={adx}")
                return None

            # Calculate trade size based on volatility
            trade_size = (volatility * 50) / current_price
            if trade_size * current_price < self.min_order_value:
                logger.warning(f"Trade size {trade_size} for {symbol} below minimum order value {self.min_order_value}")
                return None

            signal = {
                'symbol': symbol,
                'strategy': 'trend',
                'signal': signal_type,
                'entry_price': current_price,
                'trade_size': trade_size,
                'timeframe': timeframe,
                'limit': limit,
                'exchange_name': exchange_name
            }
            logger.info(f"Generated trend signal: {signal}")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate trend signal for {symbol}: {str(e)}")
            return None
