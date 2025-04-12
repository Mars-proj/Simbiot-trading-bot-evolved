from trading_bot.logging_setup import setup_logging
from .market_data import MarketData

logger = setup_logging('price_fetcher')

class PriceFetcher:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.market_data = MarketData(market_state)

    def fetch_price(self, symbol: str, exchange_name: str = 'binance') -> float:
        """Fetch the current price for a symbol."""
        try:
            klines = self.market_data.get_klines(symbol, '1m', 1, exchange_name)  # Последняя минута
            if not klines:
                logger.warning(f"No price data for {symbol} on {exchange_name}")
                return 0.0

            price = klines[-1]['close']
            logger.info(f"Fetched price for {symbol} from {exchange_name}: {price}")
            return price
        except Exception as e:
            logger.error(f"Failed to fetch price for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    fetcher = PriceFetcher(market_state)
    symbols = fetcher.market_data.get_symbols('binance')[:2]  # Первые 2 символа для теста
    for symbol in symbols:
        price = fetcher.fetch_price(symbol)
        print(f"Price for {symbol}: {price}")
