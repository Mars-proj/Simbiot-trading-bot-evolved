import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from utils.logging_setup import setup_logging
from .bollinger_strategy import BollingerStrategy
from .rsi_strategy import RSIStrategy
from .macd_strategy import MACDStrategy
from .ml_strategy import MLStrategy
from .arbitrage_strategy import ArbitrageStrategy

logger = setup_logging('strategy_manager')

class StrategyManager:
    def __init__(self, market_state: dict, market_data):
        self.market_state = market_state
        self.market_data = market_data
        self.strategies = {
            'bollinger': BollingerStrategy(market_state, market_data=market_data),
            'rsi': RSIStrategy(market_state, market_data=market_data),
            'macd': MACDStrategy(market_state, market_data=market_data),
            'ml': MLStrategy(market_state, market_data=market_data),
            'arbitrage': ArbitrageStrategy(market_state, market_data=market_data)
        }

    async def generate_signal(self, symbol: str, strategy_name: str, timeframe: str, limit: int, exchange_name: str, predictions=None, volatility=None) -> str:
        """Generate a trading signal for a symbol using the specified strategy."""
        try:
            # Адаптируем timeframe
            supported_timeframes = await self.market_data.get_supported_timeframes(exchange_name, symbol)
            if not supported_timeframes:
                logger.error(f"No supported timeframes for {exchange_name}, using default '1m'")
                timeframe = '1m'
            elif timeframe not in supported_timeframes:
                logger.warning(f"Timeframe {timeframe} not supported on {exchange_name}, using {supported_timeframes[0]}")
                timeframe = supported_timeframes[0]

            if strategy_name not in self.strategies:
                logger.error(f"Strategy {strategy_name} not found")
                return 'hold'

            strategy = self.strategies[strategy_name]
            signal = await strategy.generate_signal(symbol, timeframe, limit, exchange_name, predictions=predictions, volatility=volatility)
            logger.info(f"Generated signal for {symbol} with {strategy_name}: {signal}")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate signal for {symbol} with {strategy_name}: {str(e)}")
            return 'hold'

    async def generate_signals(self, symbol: str, strategies: list, timeframe: str, limit: int, exchange_name: str, predictions=None, volatility=None) -> dict:
        """Generate signals for a symbol using multiple strategies."""
        # Адаптируем timeframe
        supported_timeframes = await self.market_data.get_supported_timeframes(exchange_name, symbol)
        if not supported_timeframes:
            logger.error(f"No supported timeframes for {exchange_name}, using default '1m'")
            timeframe = '1m'
        elif timeframe not in supported_timeframes:
            logger.warning(f"Timeframe {timeframe} not supported on {exchange_name}, using {supported_timeframes[0]}")
            timeframe = supported_timeframes[0]

        signals = {}
        for strategy in strategies:
            signal = await self.generate_signal(symbol, strategy, timeframe, limit, exchange_name, predictions, volatility)
            signals[strategy] = signal
        logger.info(f"Generated signals: {signals}")
        return signals
