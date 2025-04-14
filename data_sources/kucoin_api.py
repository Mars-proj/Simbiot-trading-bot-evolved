from utils.logging_setup import setup_logging

logger = setup_logging('kucoin_api')

class KuCoinAPI:
    def __init__(self):
        pass

    def fetch_symbols(self):
        logger.info("Fetching symbols from KuCoin")
        return ["BTCUSDT", "ETHUSDT"]  # Пример
