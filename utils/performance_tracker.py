import time
from trading_bot.logging_setup import setup_logging
from trading_bot.utils.config_loader import load_config

logger = setup_logging('performance_tracker')

class PerformanceTracker:
    def __init__(self, market_state: dict):
        self.start_time = None
        self.operations = 0
        self.volatility = market_state['volatility']
        # Динамическая частота логирования: реже при высокой волатильности
        self.log_interval = 60 * (1 + self.volatility)  # e.g., 60 to 78 seconds
        self.last_log_time = time.time()

    def start(self):
        """Start tracking performance."""
        self.start_time = time.time()
        self.operations = 0
        logger.info("Started performance tracking")

    def record_operation(self):
        """Record a single operation."""
        self.operations += 1
        # Логируем производительность с динамической частотой
        current_time = time.time()
        if current_time - self.last_log_time >= self.log_interval:
            self.log_metrics()
            self.last_log_time = current_time

    def log_metrics(self):
        """Log performance metrics."""
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        ops_per_second = self.operations / elapsed_time if elapsed_time > 0 else 0
        logger.info(f"Performance: {self.operations} operations, {ops_per_second:.2f} ops/sec, elapsed {elapsed_time:.2f} sec")

    def get_metrics(self) -> dict:
        """Get performance metrics."""
        try:
            elapsed_time = time.time() - self.start_time if self.start_time else 0
            ops_per_second = self.operations / elapsed_time if elapsed_time > 0 else 0
            metrics = {
                "elapsed_time": elapsed_time,
                "operations": self.operations,
                "ops_per_second": ops_per_second
            }
            logger.info(f"Performance metrics: {metrics}")
            return metrics
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    tracker = PerformanceTracker(market_state)
    tracker.start()
    for i in range(1000):
        tracker.record_operation()
    metrics = tracker.get_metrics()
    print(f"Metrics: {metrics}")
