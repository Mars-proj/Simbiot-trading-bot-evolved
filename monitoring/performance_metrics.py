from trading_bot.logging_setup import setup_logging
from trading_bot.utils.performance_tracker import PerformanceTracker

logger = setup_logging('performance_metrics')

class PerformanceMetrics:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.performance_tracker = PerformanceTracker(market_state)

    def calculate_metrics(self) -> dict:
        """Calculate performance metrics."""
        try:
            metrics = self.performance_tracker.get_metrics()
            
            # Adjust metrics based on volatility
            adjusted_metrics = {}
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    adjusted_metrics[key] = value * (1 + self.volatility / 2)
                else:
                    adjusted_metrics[key] = value

            logger.info(f"Calculated performance metrics: {adjusted_metrics}")
            return adjusted_metrics
        except Exception as e:
            logger.error(f"Failed to calculate metrics: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    performance_metrics = PerformanceMetrics(market_state)
    metrics = performance_metrics.calculate_metrics()
    print(f"Performance metrics: {metrics}")
