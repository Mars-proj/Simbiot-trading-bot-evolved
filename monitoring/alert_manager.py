from utils.logging_setup import setup_logging

logger = setup_logging('alert_manager')

class AlertManager:
    def __init__(self):
        pass

    def send_alert(self, message):
        logger.info(f"Sending alert: {message}")
