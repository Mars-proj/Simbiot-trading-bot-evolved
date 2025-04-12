import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_setup import setup_logging

logger = setup_logging('strategy')

class Strategy:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']

    async def generate_signal(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'mexc') -> str:
        """Base method to generate a trading signal."""
        raise NotImplementedError("generate_signal method must be implemented in subclass")
