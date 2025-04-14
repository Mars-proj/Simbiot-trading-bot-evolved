from utils.logging_setup import setup_logging

logger = setup_logging('coinbase_api')

class CoinbaseAPI:
    def __init__(self):
        pass

    def fetch_symbols(self):
        logger.info("Fetching symbols from Coinbase")
        return ["BTCUSD", "ETHUSD"]  # Пример
