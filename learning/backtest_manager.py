import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from utils.logging_setup import setup_logging
from .backtester import Backtester

logger = setup_logging('backtest_manager')

class BacktestManager:
    def __init__(self, market_state: dict, market_data):
        self.volatility = market_state['volatility']
        self.backtester = Backtester(market_state, market_data=market_data)

    async def manage_backtests(self, symbols: list, strategies: list, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'mexc') -> dict:
        """Manage backtesting for multiple symbols and strategies."""
        try:
            results = {}
            for symbol in symbols:
                symbol_results = {}
                for strategy in strategies:
                    result = await self.backtester.run_backtest([symbol], strategy, timeframe, limit, exchange_name)
                    symbol_results[strategy] = result[symbol]
                results[symbol] = symbol_results
            logger.info(f"Backtest results: {results}")
            return results
        except Exception as e:
            logger.error(f"Failed to manage backtests: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    import asyncio
    from symbol_filter import SymbolFilter
    from data_sources.market_data import MarketData
    market_state = {'volatility': 0.3}
    market_data = MarketData(market_state)
    manager = BacktestManager(market_state, market_data=market_data)
    symbol_filter = SymbolFilter(market_state, market_data=market_data)
    
    async def main():
        # Получаем символы
        symbols = await market_data.get_symbols('mexc')
        symbols = await symbol_filter.filter_symbols(['BTC/USDT', 'ETH/USDT'], 'mexc')
        strategies = ['rsi', 'bollinger']
        
        # Run backtests
        results = await manager.manage_backtests(symbols, strategies, '1h', 30, 'mexc')
        print(f"Backtest results: {results}")

    asyncio.run(main())
