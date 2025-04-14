from utils.logging_setup import setup_logging

logger = setup_logging('health_checker')

class HealthChecker:
    def __init__(self):
        pass

    def check(self):
        logger.info("Checking system health")
        return True
