import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('mean_reversion_strategy')

class MeanReversionStrategy(Strategy):
    def __init__(self, market_state, market_data, volatility_analyzer):
        super().__init__(market_state, market_data)
        self.volatility_analyzer = volatility_analyzer
        self.min_order_value = 10.50  # $10 + 5% (hard threshold)

    async def generate_signal(self, symbol: str, timeframe: str, limit: int, exchange_name: str, klines=None):
        """Generate a mean reversion signal."""
        try:
            if klines is None:
                klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines or len(klines) < 20:
                logger.warning(f"Insufficient klines data for {symbol}")
                return None

            prices = np.array([kline[4] for kline in klines])  # Closing prices
            volatility = self.volatility_analyzer.get_volatility(symbol, timeframe, limit, exchange_name)
            
            # Dynamic period and deviation threshold based on volatility
            period = int(20 * (1 + volatility))  # Adjust period dynamically
            deviation_threshold = 2 * volatility  # Dynamic threshold

            # Calculate mean and standard deviation
            mean = np.mean(prices[-period:])
            std = np.std(prices[-period:])
            current_price = prices[-1]

            # Generate signal
            if current_price > mean + deviation_threshold * std:
                signal_type = 'sell'
            elif current_price < mean - deviation_threshold * std:
                signal_type = 'buy'
            else:
                logger.info(f"No mean reversion signal for {symbol}, price within bounds")
                return None

            # Calculate trade size based on deviation and volatility
            deviation = abs(current_price - mean) / std
            trade_size = deviation * (1 + volatility) * 50  # Dynamic trade size
            if trade_size * current_price < self.min_order_value:
                logger.warning(f"Trade size {trade_size} for {symbol} below minimum order value {self.min_order_value}")
                return None

            signal = {
                'symbol': symbol,
                'strategy': 'mean_reversion',
                'signal': signal_type,
                'entry_price': current_price,
                'trade_size': trade_size,
                'timeframe': timeframe,
                'limit': limit,
                'exchange_name': exchange_name
            }
            logger.info(f"Generated mean reversion signal: {signal}")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate mean reversion signal for {symbol}: {str(e)}")
            return None
