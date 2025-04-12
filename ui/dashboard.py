from trading_bot.logging_setup import setup_logging
from trading_bot.utils.performance_tracker import PerformanceTracker

logger = setup_logging('dashboard')

class Dashboard:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.performance_tracker = PerformanceTracker(market_state)

    def display_metrics(self) -> None:
        """Display metrics on the dashboard."""
        try:
            metrics = self.performance_tracker.get_metrics()
            print("=== Trading Dashboard ===")
            for key, value in metrics.items():
                print(f"{key}: {value}")
            print("=======================")
            logger.info("Displayed dashboard metrics")
        except Exception as e:
            logger.error(f"Failed to display metrics: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    dashboard = Dashboard(market_state)
    dashboard.display_metrics()
