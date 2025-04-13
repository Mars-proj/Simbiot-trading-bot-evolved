import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_setup import setup_logging
from utils.performance_tracker import PerformanceTracker

logger = setup_logging('monitoring')

class Monitoring:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.performance_tracker = PerformanceTracker(market_state)

    def run_monitoring(self) -> dict:
        """Run system monitoring and return metrics."""
        try:
            metrics = self.performance_tracker.get_metrics()
            logger.info(f"Monitoring metrics: {metrics}")
            return metrics
        except Exception as e:
            logger.error(f"Failed to run monitoring: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    monitoring = Monitoring(market_state)
    metrics = monitoring.run_monitoring()
    print(f"Monitoring metrics: {metrics}")
