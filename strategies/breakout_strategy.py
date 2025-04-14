import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('breakout_strategy')

class BreakoutStrategy(Strategy):
    def __init__(self, market_state, market_data, volatility_analyzer):
        super().__init__(market_state, market_data, volatility_analyzer)
        self.min_order_value = 10.50  # $10 + 5% (hard threshold)

    async def generate_signal(self, symbol: str, timeframe: str, limit: int, exchange_name: str, klines=None):
        """Generate a breakout signal."""
        try:
            if klines is None:
                klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines or len(klines) < 50:
                logger.warning(f"Insufficient klines data for {symbol}")
                return None

            prices = np.array([kline[4] for kline in klines])  # Closing prices
            volatility = self.volatility_analyzer.get_volatility(symbol, timeframe, limit, exchange_name)

            # Dynamic breakout period and threshold based on volatility
            breakout_period = int(50 * (1 + volatility / 2))
            confirmation_threshold = 1.5 * volatility

            # Calculate breakout levels
            high = np.max(prices[-breakout_period:])
            low = np.min(prices[-breakout_period:])
            current_price = prices[-1]

            # Calculate ATR (Average True Range) for confirmation
            tr = np.array([max(kline[2] - kline[3], abs(kline[2] - kline[4]), abs(kline[3] - kline[4])) for kline in klines[-14:]])
            atr = np.mean(tr)

            # Generate signal
            if current_price > high + confirmation_threshold * atr:
                signal_type = 'buy'
            elif current_price < low - confirmation_threshold * atr:
                signal_type = 'sell'
            else:
                logger.info(f"No breakout signal for {symbol}, price within range")
                return None

            # Calculate trade size based on volatility
            trade_size = (volatility * 50) / current_price
            if trade_size * current_price < self.min_order_value:
                logger.warning(f"Trade size {trade_size} for {symbol} below minimum order value {self.min_order_value}")
                return None

            signal = {
                'symbol': symbol,
                'strategy': 'breakout',
                'signal': signal_type,
                'entry_price': current_price,
                'trade_size': trade_size,
                'timeframe': timeframe,
                'limit': limit,
                'exchange_name': exchange_name
            }
            logger.info(f"Generated breakout signal: {signal}")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate breakout signal for {symbol}: {str(e)}")
            return None
