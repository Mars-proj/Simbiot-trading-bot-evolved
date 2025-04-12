from trading_bot.logging_setup import setup_logging
from .alert_manager import AlertManager
from .health_checker import HealthChecker
from .performance_monitor import PerformanceMonitor

logger = setup_logging('monitoring')

class Monitoring:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.alert_manager = AlertManager(market_state)
        self.health_checker = HealthChecker(market_state)
        self.performance_monitor = PerformanceMonitor(market_state)

    def run_monitoring(self) -> dict:
        """Run the monitoring process."""
        try:
            # Check system health
            health_status = self.health_checker.check_health()
            
            # Monitor performance
            performance_metrics = self.performance_monitor.monitor_performance()
            
            # Prepare monitoring result
            result = {
                'health': health_status,
                'performance': performance_metrics
            }
            
            # Send alerts if necessary
            if not health_status['is_healthy']:
                alert_message = f"System Health Alert: {health_status['details']}"
                self.alert_manager.send_alert(alert_message)

            logger.info(f"Monitoring result: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to run monitoring: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    monitoring = Monitoring(market_state)
    result = monitoring.run_monitoring()
    print(f"Monitoring result: {result}")
