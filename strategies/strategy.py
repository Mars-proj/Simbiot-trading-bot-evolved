import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from utils.logging_setup import setup_logging

logger = setup_logging('strategy')

class Strategy:
    def __init__(self, market_state: dict, market_data=None):
        self.volatility = market_state['volatility']
        self.market_data = market_data

    async def generate_signal(self, symbol: str, timeframe: str, limit: int, exchange_name: str) -> str:
        """Generate a trading signal."""
        raise NotImplementedError("Subclasses should implement this method")
