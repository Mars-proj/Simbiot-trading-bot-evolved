from strategies import Strategy
import random
from logging_setup import setup_logging

logger = setup_logging('strategy_generator')

def generate_strategy() -> Strategy:
    """Generate a new strategy with random type and parameters."""
    try:
        strategy_types = ['trend', 'countertrend', 'scalping']
        strategy_type = random.choice(strategy_types)
        params = {
            "threshold": random.uniform(5000, 15000),
            "stop_loss": random.uniform(0.01, 0.05),
            "take_profit": random.uniform(0.02, 0.10),
            "strategy_type": strategy_type
        }
        strategy_name = f"{strategy_type}_strategy_{random.randint(1000, 9999)}"
        logger.info(f"Generated strategy: {strategy_name} with type {strategy_type}")
        return Strategy(strategy_name, params)
    except Exception as e:
        logger.error(f"Failed to generate strategy: {str(e)}")
        raise
