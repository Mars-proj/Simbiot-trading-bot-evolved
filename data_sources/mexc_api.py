import ccxt
from utils.logging_setup import setup_logging

logger = setup_logging('mexc_api')

class MEXCAPI:
    def __init__(self):
        self.exchange = ccxt.mexc({
            'enableRateLimit': True,
        })
        logger.info("MEXCAPI initialized")
        self.symbols = None

    def fetch_symbols(self):
        """Fetch tradable symbols from MEXC."""
        try:
            markets = self.exchange.load_markets()
            symbols = [market['symbol'] for market in markets.values() if market['active']]
            # Удаляем дубликаты и сортируем
            symbols = sorted(list(set(symbols)))
            logger.info(f"Fetched {len(symbols)} symbols from MEXC")
            self.symbols = symbols
            return symbols
        except Exception as e:
            logger.error(f"Failed to fetch symbols from MEXC: {str(e)}")
            return []
