from utils.logging_setup import setup_logging

logger = setup_logging('rsi_strategy')

class RSIStrategy:
    def __init__(self, period=14, overbought=70, oversold=30, adx_threshold=25):
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        self.adx_threshold = adx_threshold

    def generate_signal(self, klines):
        logger.info("Generating RSI signal")
        return "buy"  # Пример
