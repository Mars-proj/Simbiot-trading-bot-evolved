from trading_bot.logging_setup import setup_logging
from .genetic_optimizer import GeneticOptimizer
from .backtester import Backtester

logger = setup_logging('strategy_optimizer')

class StrategyOptimizer:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.optimizer = GeneticOptimizer(market_state)
        self.backtester = Backtester(market_state)

    def optimize_strategy(self, klines: list, strategy_name: str, param_ranges: dict) -> dict:
        """Optimize strategy parameters using genetic algorithm."""
        try:
            def fitness_function(params):
                # Запускаем бэктест с текущими параметрами
                result = self.backtester.run_backtest(klines, strategy_name)
                return result['profit']  # Фитнес — это прибыль

            # Оптимизируем параметры
            best_params = self.optimizer.optimize(param_ranges, fitness_function)
            logger.info(f"Optimized parameters for {strategy_name}: {best_params}")
            return best_params
        except Exception as e:
            logger.error(f"Failed to optimize strategy {strategy_name}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    optimizer = StrategyOptimizer(market_state)
    klines = [{'timestamp': i, 'close': float(50000 + i * 100)} for i in range(30)]
    param_ranges = {
        'period': (10, 30),
        'std_dev': (1.5, 2.5)
    }
    best_params = optimizer.optimize_strategy(klines, 'bollinger', param_ranges)
    print(f"Best parameters: {best_params}")
