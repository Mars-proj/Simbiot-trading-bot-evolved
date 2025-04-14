from utils.logging_setup import setup_logging

logger = setup_logging('bybit_api')

class BybitAPI:
    def __init__(self):
        pass

    def fetch_symbols(self):
        logger.info("Fetching symbols from Bybit")
        return ["BTCUSDT", "ETHUSDT"]  # Пример
