from trading_bot.logging_setup import setup_logging
from trading_bot.learning.backtester import Backtester
from trading_bot.data_sources.market_data import MarketData

logger = setup_logging('backtest_cycle')

class BacktestCycle:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.backtester = Backtester(market_state)
        self.market_data = MarketData(market_state)

    def run_cycle(self, symbols: list, strategies: list, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'binance') -> dict:
        """Run a backtest cycle for multiple strategies."""
        try:
            results = {}
            for strategy in strategies:
                result = self.backtester.run_backtest(symbols, strategy, timeframe, limit, exchange_name)
                
                # Динамическая корректировка результатов на основе волатильности
                adjusted_result = {
                    symbol: {
                        'profit': r['profit'] * (1 - self.volatility / 2),
                        'final_balance': r['final_balance'],
                        'positions': r['positions']
                    }
                    for symbol, r in result.items()
                }
                results[strategy] = adjusted_result
            
            logger.info(f"Backtest cycle completed: {results}")
            return results
        except Exception as e:
            logger.error(f"Failed to run backtest cycle: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    from trading_bot.symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    cycle = BacktestCycle(market_state)
    symbol_filter = SymbolFilter(market_state)
    
    # Получаем символы
    symbols = symbol_filter.filter_symbols(cycle.market_data.get_symbols('binance'), 'binance')
    
    strategies = ['bollinger', 'rsi']
    results = cycle.run_cycle(symbols[:2], strategies, '1h', 30, 'binance')
    print(f"Backtest cycle results: {results}")
