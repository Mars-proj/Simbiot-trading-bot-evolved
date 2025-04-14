from utils.logging_setup import setup_logging

logger = setup_logging('signal_generator')

class SignalGenerator:
    def __init__(self):
        pass

    def generate(self, klines):
        logger.info("Generating signal")
        return "buy"  # Пример
