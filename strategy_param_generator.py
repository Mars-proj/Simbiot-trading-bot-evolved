from typing import Dict
import random

def generate_params() -> Dict:
    """Generate parameters for a strategy."""
    return {
        "threshold": random.uniform(5000, 15000),
        "stop_loss": random.uniform(0.01, 0.05),
        "take_profit": random.uniform(0.02, 0.10)
    }
