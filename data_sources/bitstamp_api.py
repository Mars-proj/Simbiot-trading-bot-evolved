from utils.logging_setup import setup_logging

logger = setup_logging('bitstamp_api')

class BitstampAPI:
    def __init__(self):
        pass

    def fetch_symbols(self):
        logger.info("Fetching symbols from Bitstamp")
        return ["BTCUSD", "ETHUSD"]  # Пример
