from utils.logging_setup import setup_logging

logger = setup_logging('trend_strategy')

class TrendStrategy:
    def __init__(self):
        pass

    def generate_signal(self, klines):
        logger.info("Generating trend signal")
        return "buy"  # Пример
