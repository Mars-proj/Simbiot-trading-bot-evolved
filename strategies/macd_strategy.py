import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('macd_strategy')

class MACDStrategy(Strategy):
    def __init__(self, market_state, market_data, volatility_analyzer):
        super().__init__(market_state, market_data, volatility_analyzer)
        self.min_order_value = 10.50  # $10 + 5% (hard threshold)

    async def generate_signal(self, symbol: str, timeframe: str, limit: int, exchange_name: str, klines=None):
        """Generate a MACD signal."""
        try:
            if klines is None:
                klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines or len(klines) < 26:
                logger.warning(f"Insufficient klines data for {symbol}")
                return None

            prices = np.array([kline[4] for kline in klines])  # Closing prices
            volatility = self.volatility_analyzer.get_volatility(symbol, timeframe, limit, exchange_name)

            # Dynamic MACD periods based on volatility
            fast_period = int(12 * (1 + volatility / 2))
            slow_period = int(26 * (1 + volatility / 2))
            signal_period = int(9 * (1 + volatility / 2))

            # Calculate MACD
            exp1 = np.convolve(prices, np.ones(fast_period)/fast_period, mode='valid')
            exp2 = np.convolve(prices, np.ones(slow_period)/slow_period, mode='valid')
            macd = exp1[-len(exp2):] - exp2
            signal_line = np.convolve(macd, np.ones(signal_period)/signal_period, mode='valid')
            macd = macd[-len(signal_line):]
            current_macd = macd[-1]
            current_signal = signal_line[-1]

            # Generate signal
            if current_macd > current_signal:
                signal_type = 'buy'
            elif current_macd < current_signal:
                signal_type = 'sell'
            else:
                logger.info(f"No MACD signal for {symbol}, MACD={current_macd}, Signal={current_signal}")
                return None

            # Calculate trade size based on volatility
            trade_size = (volatility * 50) / prices[-1]
            if trade_size * prices[-1] < self.min_order_value:
                logger.warning(f"Trade size {trade_size} for {symbol} below minimum order value {self.min_order_value}")
                return None

            signal = {
                'symbol': symbol,
                'strategy': 'macd',
                'signal': signal_type,
                'entry_price': prices[-1],
                'trade_size': trade_size,
                'timeframe': timeframe,
                'limit': limit,
                'exchange_name': exchange_name
            }
            logger.info(f"Generated MACD signal: {signal}")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate MACD signal for {symbol}: {str(e)}")
            return None
