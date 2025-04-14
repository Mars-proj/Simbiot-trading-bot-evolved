from utils.logging_setup import setup_logging

logger = setup_logging('performance_monitor')

class PerformanceMonitor:
    def __init__(self):
        pass

    def monitor(self):
        logger.info("Monitoring performance")
        return True
