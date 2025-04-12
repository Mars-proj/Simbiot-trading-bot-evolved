from trading_bot.logging_setup import setup_logging
from trading_bot.utils.performance_tracker import PerformanceTracker

logger = setup_logging('health_checker')

class HealthChecker:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.performance_tracker = PerformanceTracker(market_state)

    def check_health(self) -> dict:
        """Check the health of the system."""
        try:
            # Получаем метрики производительности
            metrics = self.performance_tracker.get_metrics()
            
            # Динамическая корректировка порогов на основе волатильности
            latency_threshold = 100 * (1 + self.volatility)  # Порог задержки в мс
            error_threshold = 0.05 * (1 + self.volatility)  # Порог ошибок
            
            health_status = {
                'latency': metrics['latency'] < latency_threshold,
                'error_rate': metrics['error_rate'] < error_threshold,
                'system_uptime': metrics['uptime'] > 0
            }
            
            overall_health = all(health_status.values())
            health_status['overall'] = overall_health
            
            logger.info(f"System health check: {health_status}")
            return health_status
        except Exception as e:
            logger.error(f"Failed to check system health: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    checker = HealthChecker(market_state)
    health_status = checker.check_health()
    print(f"Health status: {health_status}")
