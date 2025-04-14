from utils.logging_setup import setup_logging

logger = setup_logging('mean_reversion_strategy')

class MeanReversionStrategy:
    def __init__(self):
        pass

    def generate_signal(self, klines):
        logger.info("Generating mean reversion signal")
        return "buy"  # Пример
