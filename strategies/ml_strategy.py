import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('ml_strategy')

class MLStrategy(Strategy):
    def __init__(self, market_state, market_data, volatility_analyzer, online_learning):
        super().__init__(market_state, market_data, volatility_analyzer)
        self.online_learning = online_learning
        self.min_order_value = 10.50  # $10 + 5% (hard threshold)

    async def generate_signal(self, symbol: str, timeframe: str, limit: int, exchange_name: str, klines=None):
        """Generate an ML-based signal."""
        try:
            if klines is None:
                klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines or len(klines) < 20:
                logger.warning(f"Insufficient klines data for {symbol}")
                return None

            current_price = klines[-1][4]
            volatility = self.volatility_analyzer.get_volatility(symbol, timeframe, limit, exchange_name)

            # Get ML prediction
            prediction = await self.online_learning.predict(symbol, timeframe, limit, exchange_name)
            if prediction is None:
                logger.warning(f"No ML prediction for {symbol}")
                return None

            # Generate signal based on prediction
            if prediction > current_price * (1 + volatility * 0.01):
                signal_type = 'buy'
            elif prediction < current_price * (1 - volatility * 0.01):
                signal_type = 'sell'
            else:
                logger.info(f"No ML signal for {symbol}, prediction={prediction}, current_price={current_price}")
                return None

            # Calculate trade size based on volatility
            trade_size = (volatility * 50) / current_price
            if trade_size * current_price < self.min_order_value:
                logger.warning(f"Trade size {trade_size} for {symbol} below minimum order value {self.min_order_value}")
                return None

            signal = {
                'symbol': symbol,
                'strategy': 'ml',
                'signal': signal_type,
                'entry_price': current_price,
                'trade_size': trade_size,
                'timeframe': timeframe,
                'limit': limit,
                'exchange_name': exchange_name
            }
            logger.info(f"Generated ML signal: {signal}")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate ML signal for {symbol}: {str(e)}")
            return None
