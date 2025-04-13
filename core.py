import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from utils.logging_setup import setup_logging
from strategies.strategy_manager import StrategyManager
from learning.online_learning import OnlineLearning
from volatility_analyzer import VolatilityAnalyzer  # Абсолютный импорт
from symbol_filter import SymbolFilter

logger = setup_logging('core')

class TradingBotCore:
    def __init__(self, market_state: dict, market_data):
        self.strategy_manager = StrategyManager(market_state, market_data=market_data)
        self.online_learning = OnlineLearning(market_state, market_data=market_data)
        self.volatility_analyzer = VolatilityAnalyzer(market_state, market_data=market_data)
        self.symbol_filter = SymbolFilter(market_data)

    async def run_trading(self, symbol: str, strategies: list, balance: float, timeframe: str, limit: int, exchange_name: str) -> list:
        """Run trading for a single symbol."""
        try:
            trades = []
            for strategy in strategies:
                try:
                    signal = await self.strategy_manager.generate_signal(symbol, strategy, timeframe, limit, exchange_name)
                    if signal in ['buy', 'sell']:
                        trade = {'symbol': symbol, 'strategy': strategy, 'signal': signal, 'balance': balance}
                        trades.append(trade)
                except Exception as e:
                    logger.warning(f"Error generating signal for {symbol} with {strategy}: {str(e)}")
                    continue

            # Retrain models with online learning
            await self.online_learning.retrain(symbol, timeframe, limit, exchange_name)

            logger.info(f"Trading completed: {trades}")
            return trades
        except Exception as e:
            logger.error(f"Error in trading for {symbol}: {str(e)}")
            return []

    async def filter_symbols(self, symbols: list, exchange_name: str, timeframe: str) -> list:
        """Filter symbols using SymbolFilter."""
        return await self.symbol_filter.filter_symbols(symbols, exchange_name, timeframe)
