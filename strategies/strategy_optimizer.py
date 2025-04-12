from trading_bot.logging_setup import setup_logging
from trading_bot.learning.genetic_optimizer import GeneticOptimizer
from trading_bot.strategies.strategy import Strategy

logger = setup_logging('strategy_optimizer')

def optimize_strategy(strategy: Strategy, symbols: list, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'binance') -> dict:
    """Optimize a strategy using genetic optimization."""
    try:
        logger.info(f"Starting optimization for strategy {strategy.name}")
        optimizer = GeneticOptimizer({'volatility': strategy.volatility}, population_size=50, generations=10)
        best_params = optimizer.optimize(strategy, symbols, timeframe, limit, exchange_name)
        logger.info(f"Optimization completed. Best parameters: {best_params}")
        return best_params
    except Exception as e:
        logger.error(f"Optimization failed: {str(e)}")
        raise

if __name__ == "__main__":
    # Test run
    from trading_bot.strategies.bollinger_strategy import BollingerStrategy
    from trading_bot.symbol_filter import SymbolFilter
    from trading_bot.data_sources.market_data import MarketData
    market_state = {'volatility': 0.3}
    strategy = BollingerStrategy(market_state)
    symbol_filter = SymbolFilter(market_state)
    market_data = MarketData(market_state)
    
    # Получаем символы
    symbols = symbol_filter.filter_symbols(market_data.get_symbols('binance'), 'binance')
    
    if symbols:
        best_params = optimize_strategy(strategy, symbols[:2], '1h', 30, 'binance')
        print(f"Best parameters: {best_params}")
    else:
        print("No symbols available for testing")
