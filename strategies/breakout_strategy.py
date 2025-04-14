from utils.logging_setup import setup_logging

logger = setup_logging('breakout_strategy')

class BreakoutStrategy:
    def __init__(self):
        pass

    def generate_signal(self, klines):
        logger.info("Generating breakout signal")
        return "buy"  # Пример
