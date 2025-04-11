import psutil
import time
from notification_manager import notify
from logging_setup import setup_logging

logger = setup_logging('monitoring')

class PerformanceMonitor:
    def __init__(self, alert_thresholds: dict):
        self.alert_thresholds = alert_thresholds  # e.g., {"cpu": 80, "memory": 80}

    def monitor(self):
        """Monitor system performance and send alerts if thresholds are exceeded."""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent

            if cpu_usage > self.alert_thresholds["cpu"]:
                message = f"High CPU usage detected: {cpu_usage}%"
                notify(message, channel="telegram")
                logger.warning(message)

            if memory_usage > self.alert_thresholds["memory"]:
                message = f"High memory usage detected: {memory_usage}%"
                notify(message, channel="telegram")
                logger.warning(message)

            logger.info(f"Performance: CPU={cpu_usage}%, Memory={memory_usage}%")
            return {"cpu_usage": cpu_usage, "memory_usage": memory_usage}
        except Exception as e:
            logger.error(f"Monitoring failed: {str(e)}")
            raise
