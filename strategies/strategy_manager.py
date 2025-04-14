import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import numpy as np
from utils.logging_setup import setup_logging
from .bollinger_strategy import BollingerStrategy
from .rsi_strategy import RSIStrategy
from .macd_strategy import MACDStrategy
from .ml_strategy import MLStrategy
from .arbitrage_strategy import ArbitrageStrategy
from .mean_reversion_strategy import MeanReversionStrategy
from .grid_strategy import GridStrategy

logger = setup_logging('strategy_manager')

class StrategyManager:
    def __init__(self, market_state, market_data):
        self.market_state = market_state
        self.market_data = market_data
        self.strategies = [
            BollingerStrategy(market_state, market_data),
            RSIStrategy(market_state, market_data),
            MACDStrategy(market_state, market_data),
            MLStrategy(market_state, market_data),
            ArbitrageStrategy(market_state, market_data),
            MeanReversionStrategy(market_state, market_data),
            GridStrategy(market_state, market_data)
        ]

    async def generate_signals(self, symbol: str, timeframe: str, limit: int, exchange_name: str, klines=None):
        """Generate signals from all strategies."""
        try:
            signals = []
            for strategy in self.strategies:
                signal = await strategy.generate_signal(symbol, timeframe, limit, exchange_name, klines)
                if signal:
                    signals.append(signal)
            logger.info(f"Generated {len(signals)} signals for {symbol}")
            return signals
        except Exception as e:
            logger.error(f"Failed to generate signals for {symbol}: {str(e)}")
            return []
