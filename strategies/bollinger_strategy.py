from utils.logging_setup import setup_logging

logger = setup_logging('bollinger_strategy')

class BollingerStrategy:
    def __init__(self, period=20, deviation=2):
        self.period = period
        self.deviation = deviation

    def generate_signal(self, klines):
        logger.info("Generating Bollinger Bands signal")
        return "buy"  # Пример
