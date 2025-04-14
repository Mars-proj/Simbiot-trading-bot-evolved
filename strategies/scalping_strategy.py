import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('scalping_strategy')

class ScalpingStrategy(Strategy):
    def __init__(self, market_state, market_data, volatility_analyzer):
        super().__init__(market_state, market_data, volatility_analyzer)
        self.min_order_value = 10.50  # $10 + 5% (hard threshold)

    async def generate_signal(self, symbol: str, timeframe: str, limit: int, exchange_name: str, klines=None):
        """Generate a scalping signal."""
        try:
            if klines is None:
                klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines or len(klines) < 5:
                logger.warning(f"Insufficient klines data for {symbol}")
                return None

            prices = np.array([kline[4] for kline in klines])  # Closing prices
            volatility = self.volatility_analyzer.get_volatility(symbol, timeframe, limit, exchange_name)

            # Dynamic threshold based on volatility
            min_profit = 0.002 * (1 + volatility)  # 0.2% adjusted by volatility
            current_price = prices[-1]
            recent_high = np.max(prices[-5:])
            recent_low = np.min(prices[-5:])

            # Generate signal
            if current_price >= recent_high * (1 + min_profit):
                signal_type = 'sell'
            elif current_price <= recent_low * (1 - min_profit):
                signal_type = 'buy'
            else:
                logger.info(f"No scalping signal for {symbol}, price within range")
                return None

            # Calculate trade size based on volatility
            trade_size = (volatility * 50) / current_price
            if trade_size * current_price < self.min_order_value:
                logger.warning(f"Trade size {trade_size} for {symbol} below minimum order value {self.min_order_value}")
                return None

            signal = {
                'symbol': symbol,
                'strategy': 'scalping',
                'signal': signal_type,
                'entry_price': current_price,
                'trade_size': trade_size,
                'timeframe': timeframe,
                'limit': limit,
                'exchange_name': exchange_name
            }
            logger.info(f"Generated scalping signal: {signal}")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate scalping signal for {symbol}: {str(e)}")
            return None
