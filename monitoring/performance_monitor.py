from trading_bot.logging_setup import setup_logging
from .performance_metrics import PerformanceMetrics
from .alert_manager import AlertManager

logger = setup_logging('performance_monitor')

class PerformanceMonitor:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.metrics_calculator = PerformanceMetrics(market_state)
        self.alert_manager = AlertManager(market_state)

    def monitor(self):
        """Monitor system performance and send alerts if needed."""
        try:
            # Получаем метрики производительности
            metrics = self.metrics_calculator.calculate_metrics()
            
            # Проверяем метрики и отправляем оповещения при необходимости
            if metrics['adjusted_latency'] > 150:  # Порог задержки в мс
                self.alert_manager.send_alert(
                    f"High latency detected: {metrics['adjusted_latency']} ms",
                    severity='warning'
                )
            
            if metrics['adjusted_error_rate'] > 0.1:  # Порог ошибок
                self.alert_manager.send_alert(
                    f"High error rate detected: {metrics['adjusted_error_rate']}",
                    severity='error'
                )
            
            logger.info("Performance monitoring completed")
            return metrics
        except Exception as e:
            logger.error(f"Failed to monitor performance: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    monitor = PerformanceMonitor(market_state)
    metrics = monitor.monitor()
    print(f"Monitored metrics: {metrics}")
