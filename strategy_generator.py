from strategies import Strategy
import random

def generate_strategy() -> Strategy:
    """Generate a new strategy with random parameters."""
    params = {
        "threshold": random.uniform(5000, 15000),
        "stop_loss": random.uniform(0.01, 0.05),
        "take_profit": random.uniform(0.02, 0.10)
    }
    strategy_name = f"strategy_{random.randint(1000, 9999)}"
    return Strategy(strategy_name, params)
