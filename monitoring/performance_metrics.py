from trading_bot.logging_setup import setup_logging
from trading_bot.utils.performance_tracker import PerformanceTracker

logger = setup_logging('performance_metrics')

class PerformanceMetrics:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.performance_tracker = PerformanceTracker(market_state)

    def calculate_metrics(self) -> dict:
        """Calculate performance metrics for the system."""
        try:
            # Получаем базовые метрики из PerformanceTracker
            raw_metrics = self.performance_tracker.get_metrics()
            
            # Динамическая корректировка метрик на основе волатильности
            adjusted_latency = raw_metrics['latency'] * (1 + self.volatility / 2)
            adjusted_error_rate = raw_metrics['error_rate'] * (1 + self.volatility / 2)
            
            metrics = {
                'adjusted_latency': adjusted_latency,
                'adjusted_error_rate': adjusted_error_rate,
                'uptime': raw_metrics['uptime'],
                'trade_volume': raw_metrics.get('trade_volume', 0)
            }
            
            logger.info(f"Calculated performance metrics: {metrics}")
            return metrics
        except Exception as e:
            logger.error(f"Failed to calculate performance metrics: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    metrics_calculator = PerformanceMetrics(market_state)
    metrics = metrics_calculator.calculate_metrics()
    print(f"Performance metrics: {metrics}")
