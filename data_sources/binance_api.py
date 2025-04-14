from utils.logging_setup import setup_logging

logger = setup_logging('binance_api')

class BinanceAPI:
    def __init__(self):
        pass

    def fetch_symbols(self):
        logger.info("Fetching symbols from Binance")
        return ["BTCUSDT", "ETHUSDT"]  # Пример
