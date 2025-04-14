from utils.logging_setup import setup_logging

logger = setup_logging('roboforex_api')

class RoboForexAPI:
    def __init__(self):
        pass

    def fetch_symbols(self):
        logger.info("Fetching symbols from RoboForex")
        return ["EURUSD", "USDJPY"]  # Пример
