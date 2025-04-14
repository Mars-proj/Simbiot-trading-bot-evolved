import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('arbitrage_strategy')

class ArbitrageStrategy(Strategy):
    def __init__(self, market_state, market_data, volatility_analyzer):
        super().__init__(market_state, market_data)
        self.volatility_analyzer = volatility_analyzer
        self.min_order_value = 10.50  # $10 + 5% (hard threshold)

    async def generate_signal(self, symbol: str, timeframe: str, limit: int, exchange_name: str, klines=None):
        """Generate an arbitrage signal."""
        try:
            # Fetch prices from multiple exchanges
            exchanges = ['mexc', 'binance']  # Example exchanges, expand as needed
            prices = {}
            for exchange in exchanges:
                if exchange not in self.market_data.exchanges:
                    await self.market_data.initialize_exchange(exchange)
                ticker = await self.market_data.exchanges[exchange].fetch_ticker(symbol)
                prices[exchange] = ticker['last']

            # Calculate price difference
            price_diff = abs(prices['mexc'] - prices['binance'])
            volatility = self.volatility_analyzer.get_volatility(symbol, timeframe, limit, exchange_name)
            
            # Dynamic threshold based on volatility
            min_price_diff = 0.01 * (1 + volatility)  # 1% adjusted by volatility
            if price_diff < min_price_diff:
                logger.info(f"Price difference {price_diff} for {symbol} too low, skipping")
                return None

            # Determine buy and sell exchanges
            buy_exchange = 'mexc' if prices['mexc'] < prices['binance'] else 'binance'
            sell_exchange = 'binance' if prices['mexc'] < prices['binance'] else 'mexc'

            # Calculate trade size based on price difference and volatility
            trade_size = price_diff * (1 + volatility) * 100  # Dynamic trade size
            if trade_size * prices[buy_exchange] < self.min_order_value:
                logger.warning(f"Trade size {trade_size} for {symbol} below minimum order value {self.min_order_value}")
                return None

            signal = {
                'symbol': symbol,
                'strategy': 'arbitrage',
                'signal': 'buy',
                'buy_exchange': buy_exchange,
                'sell_exchange': sell_exchange,
                'entry_price': prices[buy_exchange],
                'trade_size': trade_size,
                'timeframe': timeframe,
                'limit': limit,
                'exchange_name': exchange_name
            }
            logger.info(f"Generated arbitrage signal: {signal}")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate arbitrage signal for {symbol}: {str(e)}")
            return None
