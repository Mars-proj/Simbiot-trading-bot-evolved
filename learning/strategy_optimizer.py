from genetic_optimizer import GeneticOptimizer
from strategies import Strategy
import logging

def setup_logging():
    logging.basicConfig(
        filename='optimizer.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def optimize_strategy(strategy: Strategy, data: dict) -> dict:
    """Optimize a strategy using genetic optimization."""
    setup_logging()
    try:
        logging.info(f"Starting optimization for strategy {strategy.name}")
        optimizer = GeneticOptimizer(population_size=50, generations=10)
        best_params = optimizer.optimize(strategy, data)
        logging.info(f"Optimization completed. Best parameters: {best_params}")
        return best_params
    except Exception as e:
        logging.error(f"Optimization failed: {str(e)}")
        raise
