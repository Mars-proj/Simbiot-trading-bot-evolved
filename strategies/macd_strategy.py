from utils.logging_setup import setup_logging

logger = setup_logging('macd_strategy')

class MACDStrategy:
    def __init__(self, fast_period=12, slow_period=26, signal_period=9):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def generate_signal(self, klines):
        logger.info("Generating MACD signal")
        return "buy"  # Пример
