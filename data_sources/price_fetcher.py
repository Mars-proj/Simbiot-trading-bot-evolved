from utils.logging_setup import setup_logging

logger = setup_logging('price_fetcher')

class PriceFetcher:
    def __init__(self):
        pass

    def fetch_price(self, symbol, exchange):
        logger.info(f"Fetching price for {symbol} from {exchange}")
        return 1000  # Пример
