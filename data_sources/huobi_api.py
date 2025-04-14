from utils.logging_setup import setup_logging

logger = setup_logging('huobi_api')

class HuobiAPI:
    def __init__(self):
        pass

    def fetch_symbols(self):
        logger.info("Fetching symbols from Huobi")
        return ["BTCUSDT", "ETHUSDT"]  # Пример
