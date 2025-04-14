from utils.logging_setup import setup_logging

logger = setup_logging('kraken_api')

class KrakenAPI:
    def __init__(self):
        pass

    def fetch_symbols(self):
        logger.info("Fetching symbols from Kraken")
        return ["BTCUSD", "ETHUSD"]  # Пример
