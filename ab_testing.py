from trading_bot.logging_setup import setup_logging
from trading_bot.learning.backtester import Backtester
from trading_bot.data_sources.market_data import MarketData

logger = setup_logging('ab_testing')

class ABTesting:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.backtester = Backtester(market_state)
        self.market_data = MarketData(market_state)

    def run_test(self, symbol: str, strategy_a: str, strategy_b: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'binance') -> dict:
        """Run A/B testing between two strategies."""
        try:
            # Получаем данные для символа
            klines = self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            
            # Запускаем бэктест для стратегии A
            result_a = self.backtester.run_backtest([symbol], strategy_a, timeframe, limit, exchange_name)
            
            # Запускаем бэктест для стратегии B
            result_b = self.backtester.run_backtest([symbol], strategy_b, timeframe, limit, exchange_name)
            
            # Сравниваем результаты
            comparison = {
                'strategy_a': strategy_a,
                'strategy_b': strategy_b,
                'profit_a': result_a[symbol]['profit'],
                'profit_b': result_b[symbol]['profit'],
                'winner': strategy_a if result_a[symbol]['profit'] > result_b[symbol]['profit'] else strategy_b
            }
            
            logger.info(f"A/B testing result: {comparison}")
            return comparison
        except Exception as e:
            logger.error(f"Failed to run A/B test: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    from trading_bot.symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    ab_testing = ABTesting(market_state)
    symbol_filter = SymbolFilter(market_state)
    
    # Получаем символы
    symbols = symbol_filter.filter_symbols(ab_testing.market_data.get_symbols('binance'), 'binance')
    
    # Выбираем первый символ для теста
    symbol = symbols[0] if symbols else None
    if symbol:
        result = ab_testing.run_test(symbol, 'bollinger', 'rsi', '1h', 30, 'binance')
        print(f"A/B testing result for {symbol}: {result}")
    else:
        print("No symbols available for testing")
