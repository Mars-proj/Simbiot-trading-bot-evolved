import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_setup import setup_logging
from trading_bot.utils.performance_tracker import PerformanceTracker

logger = setup_logging('trade_logger')

class TradeLogger:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.performance_tracker = PerformanceTracker(market_state)

    def log_trade(self, trade: dict) -> None:
        """Log trade details."""
        try:
            logger.info(f"Trade logged: {trade}")
            self.performance_tracker.record_request()
        except Exception as e:
            logger.error(f"Failed to log trade: {str(e)}")
            self.performance_tracker.record_error()
            raise
