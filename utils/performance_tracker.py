import time
from trading_bot.logging_setup import setup_logging

logger = setup_logging('performance_tracker')

class PerformanceTracker:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.start_time = time.time()
        self.requests = 0
        self.errors = 0
        self.total_latency = 0.0
        self.request_count_for_latency = 0

    def record_request(self, latency: float = None) -> None:
        """Record a request for performance tracking with optional latency."""
        try:
            self.requests += 1
            if latency is not None:
                self.total_latency += latency
                self.request_count_for_latency += 1
            logger.info("Recorded a request")
        except Exception as e:
            logger.error(f"Failed to record request: {str(e)}")
            raise

    def record_error(self) -> None:
        """Record an error for performance tracking."""
        try:
            self.errors += 1
            logger.info("Recorded an error")
        except Exception as e:
            logger.error(f"Failed to record error: {str(e)}")
            raise

    def get_metrics(self) -> dict:
        """Get performance metrics."""
        try:
            elapsed_time = time.time() - self.start_time
            requests_per_second = self.requests / elapsed_time if elapsed_time > 0 else 0
            error_rate = self.errors / self.requests if self.requests > 0 else 0
            avg_latency = (self.total_latency / self.request_count_for_latency) if self.request_count_for_latency > 0 else 0.0
            
            metrics = {
                'requests': self.requests,
                'errors': self.errors,
                'requests_per_second': requests_per_second,
                'error_rate': error_rate,
                'latency': avg_latency,  # Average latency in milliseconds
                'uptime': elapsed_time
            }
            
            logger.info(f"Performance metrics: {metrics}")
            return metrics
        except Exception as e:
            logger.error(f"Failed to get metrics: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    tracker = PerformanceTracker(market_state)
    
    # Simulate requests with varying latencies
    for i in range(5):
        tracker.record_request(latency=100 + i * 10)  # Simulated latency in milliseconds
        if i % 2 == 0:
            tracker.record_error()
        time.sleep(0.1)
    
    metrics = tracker.get_metrics()
    print(f"Performance metrics: {metrics}")
