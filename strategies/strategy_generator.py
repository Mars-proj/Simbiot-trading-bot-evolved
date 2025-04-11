from strategies import Strategy
from logging_setup import setup_logging
import random

logger = setup_logging('strategy_generator')

def generate_strategy(market_state: dict = None) -> Strategy:
    """Generate a new trading strategy with dynamic parameters."""
    try:
        # Dynamic parameters based on market state
        if market_state:
            volatility = market_state['volatility']
            rsi_threshold = random.uniform(60, 80) * (1 + volatility)  # Higher volatility -> higher threshold
            macd_threshold = random.uniform(-0.1, 0.1) * volatility  # Scale with volatility
        else:
            rsi_threshold = random.uniform(60, 80)
            macd_threshold = random.uniform(-0.1, 0.1)

        strategy = Strategy(name="DynamicStrategy", params={"rsi_threshold": rsi_threshold, "macd_threshold": macd_threshold})
        logger.info(f"Generated strategy: {strategy.name} with params: {strategy.params}")
        return strategy
    except Exception as e:
        logger.error(f"Failed to generate strategy: {str(e)}")
        raise
