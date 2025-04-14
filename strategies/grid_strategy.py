import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('grid_strategy')

class GridStrategy(Strategy):
    def __init__(self, market_state, market_data, volatility_analyzer):
        super().__init__(market_state, market_data)
        self.volatility_analyzer = volatility_analyzer
        self.min_order_value = 10.50  # $10 + 5% (hard threshold)

    async def generate_signal(self, symbol: str, timeframe: str, limit: int, exchange_name: str, klines=None):
        """Generate a grid trading signal."""
        try:
            if klines is None:
                klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines or len(klines) < 20:
                logger.warning(f"Insufficient klines data for {symbol}")
                return None

            prices = np.array([kline[4] for kline in klines])  # Closing prices
            volatility = self.volatility_analyzer.get_volatility(symbol, timeframe, limit, exchange_name)
            
            # Dynamic grid parameters based on volatility
            grid_size = 0.005 * (1 + volatility)  # Grid size adjusted by volatility
            levels = int(10 * (1 + volatility / 2))  # Number of grid levels
            current_price = prices[-1]

            # Calculate grid levels
            price_range = current_price * (volatility * 2)
            grid_step = price_range / levels
            grid_levels = [current_price + i * grid_step for i in range(-levels // 2, levels // 2 + 1)]

            # Find nearest grid levels
            buy_level = max([level for level in grid_levels if level < current_price], default=current_price)
            sell_level = min([level for level in grid_levels if level > current_price], default=current_price)

            # Generate signal based on price proximity to grid levels
            if abs(current_price - buy_level) < abs(current_price - sell_level):
                signal_type = 'buy'
                entry_price = buy_level
            else:
                signal_type = 'sell'
                entry_price = sell_level

            # Calculate trade size based on volatility
            trade_size = (volatility * 50) / entry_price  # Dynamic trade size
            if trade_size * entry_price < self.min_order_value:
                logger.warning(f"Trade size {trade_size} for {symbol} below minimum order value {self.min_order_value}")
                return None

            signal = {
                'symbol': symbol,
                'strategy': 'grid',
                'signal': signal_type,
                'entry_price': entry_price,
                'trade_size': trade_size,
                'timeframe': timeframe,
                'limit': limit,
                'exchange_name': exchange_name
            }
            logger.info(f"Generated grid signal: {signal}")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate grid signal for {symbol}: {str(e)}")
            return None
