import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
from .logging_setup import setup_logging

logger = setup_logging('performance_tracker')

class PerformanceTracker:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.requests = 0
        self.errors = 0
        self.start_time = time.time()

    def record_request(self) -> None:
        """Record a successful request."""
        try:
            self.requests += 1
            logger.debug(f"Recorded request. Total requests: {self.requests}")
        except Exception as e:
            logger.error(f"Failed to record request: {str(e)}")
            raise

    def record_error(self) -> None:
        """Record an error."""
        try:
            self.errors += 1
            logger.debug(f"Recorded error. Total errors: {self.errors}")
        except Exception as e:
            logger.error(f"Failed to record error: {str(e)}")
            raise

    def get_metrics(self) -> dict:
        """Get performance metrics."""
        try:
            elapsed_time = time.time() - self.start_time
            requests_per_second = self.requests / elapsed_time if elapsed_time > 0 else 0
            error_rate = self.errors / self.requests if self.requests > 0 else 0
            metrics = {
                'requests': self.requests,
                'errors': self.errors,
                'requests_per_second': requests_per_second,
                'error_rate': error_rate
            }
            logger.info(f"Performance metrics: {metrics}")
            return metrics
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    tracker = PerformanceTracker(market_state)
    tracker.record_request()
    tracker.record_error()
    metrics = tracker.get_metrics()
    print(f"Metrics: {metrics}")
