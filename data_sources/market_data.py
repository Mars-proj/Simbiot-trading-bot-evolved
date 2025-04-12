from trading_bot.logging_setup import setup_logging
from trading_bot.data_sources.binance_api import BinanceAPI
from trading_bot.data_sources.kraken_api import KrakenAPI
from trading_bot.data_sources.mexc_api import MEXCAPI

logger = setup_logging('market_data')

class MarketData:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.exchanges = {
            'binance': BinanceAPI(market_state),
            'kraken': KrakenAPI(market_state),
            'mexc': MEXCAPI(market_state)
        }

    def get_symbols(self, exchange_name: str = 'binance') -> list:
        """Get a list of available symbols from the specified exchange."""
        try:
            exchange = self.exchanges.get(exchange_name.lower())
            if not exchange:
                raise ValueError(f"Unsupported exchange: {exchange_name}")

            # Получаем символы с биржи
            symbols = exchange.get_symbols()
            logger.info(f"Retrieved {len(symbols)} symbols from {exchange_name}")
            return symbols
        except Exception as e:
            logger.error(f"Failed to get symbols from {exchange_name}: {str(e)}")
            raise

    def get_klines(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'binance') -> list:
        """Get historical klines for a symbol from the specified exchange."""
        try:
            exchange = self.exchanges.get(exchange_name.lower())
            if not exchange:
                raise ValueError(f"Unsupported exchange: {exchange_name}")

            # Получаем данные с биржи
            klines = exchange.get_klines(symbol, timeframe, limit)
            logger.info(f"Retrieved klines for {symbol} from {exchange_name}")
            return klines
        except Exception as e:
            logger.error(f"Failed to get klines for {symbol} from {exchange_name}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    market_data = MarketData(market_state)
    symbols = market_data.get_symbols('mexc')
    print(f"Symbols from MEXC: {symbols[:5]}")  # Первые 5 символов для теста
    if symbols:
        klines = market_data.get_klines(symbols[0], '1h', 30, 'mexc')
        print(f"Klines for {symbols[0]} from MEXC: {klines[:5]}")
