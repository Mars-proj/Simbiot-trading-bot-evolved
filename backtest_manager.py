from trading_bot.logging_setup import setup_logging
from trading_bot.learning.backtest_cycle import BacktestCycle
from trading_bot.data_sources.market_data import MarketData

logger = setup_logging('backtest_manager')

class BacktestManager:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.backtest_cycle = BacktestCycle(market_state)
        self.market_data = MarketData(market_state)

    def manage_backtests(self, symbols: list, strategies: list, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'binance') -> dict:
        """Manage backtesting for multiple strategies and aggregate results."""
        try:
            # Запускаем цикл бэктестинга
            cycle_results = self.backtest_cycle.run_cycle(symbols, strategies, timeframe, limit, exchange_name)
            
            # Агрегируем результаты
            aggregated_results = {}
            for strategy, result in cycle_results.items():
                aggregated_results[strategy] = {
                    symbol: {
                        'profit': r['profit'],
                        'adjusted_profit': r['profit'],  # Уже скорректировано в backtest_cycle
                        'final_balance': r['final_balance']
                    }
                    for symbol, r in result.items()
                }
            
            logger.info(f"Backtest management completed: {aggregated_results}")
            return aggregated_results
        except Exception as e:
            logger.error(f"Failed to manage backtests: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    from trading_bot.symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    manager = BacktestManager(market_state)
    symbol_filter = SymbolFilter(market_state)
    
    # Получаем символы
    symbols = symbol_filter.filter_symbols(manager.market_data.get_symbols('binance'), 'binance')
    
    strategies = ['bollinger', 'rsi', 'macd']
    results = manager.manage_backtests(symbols[:3], strategies, '1h', 30, 'binance')
    print(f"Backtest management results: {results}")
