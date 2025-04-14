from utils.logging_setup import setup_logging

logger = setup_logging('monitoring')

class Monitoring:
    def __init__(self):
        pass

    def monitor(self):
        logger.info("Monitoring system")
        return True
