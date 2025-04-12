from trading_bot.logging_setup import setup_logging
from trading_bot.utils.performance_tracker import PerformanceTracker

logger = setup_logging('performance_monitor')

class PerformanceMonitor:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.performance_tracker = PerformanceTracker(market_state)

    def monitor_performance(self) -> dict:
        """Monitor system performance."""
        try:
            # Simulate performance monitoring
            metrics = self.performance_tracker.get_metrics()
            
            # Adjust monitoring based on volatility
            adjusted_metrics = {}
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    adjusted_metrics[key] = value * (1 + self.volatility / 2)
                else:
                    adjusted_metrics[key] = value

            logger.info(f"Monitored performance: {adjusted_metrics}")
            return adjusted_metrics
        except Exception as e:
            logger.error(f"Failed to monitor performance: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    monitor = PerformanceMonitor(market_state)
    performance = monitor.monitor_performance()
    print(f"Performance: {performance}")
