from utils.logging_setup import setup_logging

logger = setup_logging('ml_strategy')

class MLStrategy:
    def __init__(self, model):
        self.model = model

    def generate_signal(self, klines):
        logger.info("Generating ML signal")
        return "buy"  # Пример
