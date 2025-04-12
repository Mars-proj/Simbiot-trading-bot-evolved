from trading_bot.logging_setup import setup_logging
from .health_checker import HealthChecker
from .performance_monitor import PerformanceMonitor

logger = setup_logging('monitoring')

class Monitoring:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.health_checker = HealthChecker(market_state)
        self.performance_monitor = PerformanceMonitor(market_state)

    def run_monitoring(self):
        """Run full system monitoring."""
        try:
            # Проверяем здоровье системы
            health_status = self.health_checker.check_health()
            
            # Мониторим производительность
            performance_metrics = self.performance_monitor.monitor()
            
            monitoring_result = {
                'health_status': health_status,
                'performance_metrics': performance_metrics
            }
            
            logger.info(f"Monitoring result: {monitoring_result}")
            return monitoring_result
        except Exception as e:
            logger.error(f"Failed to run monitoring: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    monitoring = Monitoring(market_state)
    result = monitoring.run_monitoring()
    print(f"Monitoring result: {result}")
