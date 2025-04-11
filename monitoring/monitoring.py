import psutil
from logging_setup import setup_logging

logger = setup_logging('monitoring')

class PerformanceMonitor:
    def __init__(self, market_state: dict):
        # Dynamic thresholds based on market state
        volatility = market_state['volatility']
        # Higher volatility -> stricter thresholds
        self.cpu_threshold = 80 * (1 - volatility/2)  # e.g., 80 to 60
        self.memory_threshold = 80 * (1 - volatility/2)

    def monitor(self):
        """Monitor system performance and log metrics."""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent
            logger.info(f"Performance: CPU={cpu_usage}%, Memory={memory_usage}%")
            if cpu_usage > self.cpu_threshold or memory_usage > self.memory_threshold:
                logger.warning(f"High resource usage detected: CPU={cpu_usage}%, Memory={memory_usage}%")
        except Exception as e:
            logger.error(f"Failed to monitor performance: {str(e)}")
            raise
