import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('bollinger_strategy')

class BollingerStrategy(Strategy):
    def __init__(self, market_state, market_data, volatility_analyzer):
        super().__init__(market_state, market_data, volatility_analyzer)
        self.min_order_value = 10.50  # $10 + 5% (hard threshold)

    async def generate_signal(self, symbol: str, timeframe: str, limit: int, exchange_name: str, klines=None):
        """Generate a Bollinger Bands signal."""
        try:
            if klines is None:
                klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines or len(klines) < 20:
                logger.warning(f"Insufficient klines data for {symbol}")
                return None

            prices = np.array([kline[4] for kline in klines])  # Closing prices
            volatility = self.volatility_analyzer.get_volatility(symbol, timeframe, limit, exchange_name)

            # Dynamic period and deviation based on volatility
            period = int(20 * (1 + volatility))
            deviation = 2 + volatility  # Adjust deviation dynamically

            # Calculate Bollinger Bands
            sma = np.mean(prices[-period:])
            std = np.std(prices[-period:])
            upper_band = sma + deviation * std
            lower_band = sma - deviation * std
            current_price = prices[-1]

            # Generate signal
            if current_price > upper_band:
                signal_type = 'sell'
            elif current_price < lower_band:
                signal_type = 'buy'
            else:
                logger.info(f"No Bollinger Bands signal for {symbol}, price within bounds")
                return None

            # Calculate trade size based on volatility
            trade_size = (volatility * 50) / current_price
            if trade_size * current_price < self.min_order_value:
                logger.warning(f"Trade size {trade_size} for {symbol} below minimum order value {self.min_order_value}")
                return None

            signal = {
                'symbol': symbol,
                'strategy': 'bollinger',
                'signal': signal_type,
                'entry_price': current_price,
                'trade_size': trade_size,
                'timeframe': timeframe,
                'limit': limit,
                'exchange_name': exchange_name
            }
            logger.info(f"Generated Bollinger Bands signal: {signal}")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate Bollinger Bands signal for {symbol}: {str(e)}")
            return None
