from utils.logging_setup import setup_logging

logger = setup_logging('volatility_strategy')

class VolatilityStrategy:
    def __init__(self):
        pass

    def generate_signal(self, klines):
        logger.info("Generating volatility signal")
        return "buy"  # Пример
