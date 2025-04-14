from utils.logging_setup import setup_logging

logger = setup_logging('arbitrage_strategy')

class ArbitrageStrategy:
    def __init__(self):
        pass

    def generate_signal(self, klines):
        logger.info("Generating arbitrage signal")
        return "buy"  # Пример
