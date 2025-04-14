from utils.logging_setup import setup_logging

logger = setup_logging('grid_strategy')

class GridStrategy:
    def __init__(self):
        pass

    def generate_signal(self, klines):
        logger.info("Generating grid signal")
        return "buy"  # Пример
