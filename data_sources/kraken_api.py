from trading_bot.logging_setup import setup_logging
import ccxt

logger = setup_logging('kraken_api')

class KrakenAPI:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.exchange = ccxt.kraken({
            'enableRateLimit': True,
        })

    def get_symbols(self) -> list:
        """Get a list of available symbols from Kraken."""
        try:
            markets = self.exchange.load_markets()
            symbols = [symbol for symbol in markets.keys() if symbol.endswith('/USDT')]
            logger.info(f"Retrieved {len(symbols)} symbols from Kraken")
            return symbols
        except Exception as e:
            logger.error(f"Failed to get symbols from Kraken: {str(e)}")
            raise

    def get_klines(self, symbol: str, timeframe: str = '1h', limit: int = 30) -> list:
        """Get historical klines for a symbol from Kraken."""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            klines = [
                {
                    'timestamp': candle[0] // 1000,  # Конвертируем миллисекунды в секунды
                    'open': float(candle[1]),
                    'high': float(candle[2]),
                    'low': float(candle[3]),
                    'close': float(candle[4]),
                    'volume': float(candle[5])
                }
                for candle in ohlcv
            ]
            logger.info(f"Retrieved {len(klines)} klines for {symbol} from Kraken")
            return klines
        except Exception as e:
            logger.error(f"Failed to get klines for {symbol} from Kraken: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    api = KrakenAPI(market_state)
    symbols = api.get_symbols()
    print(f"Symbols: {symbols[:5]}")  # Первые 5 символов для теста
    if symbols:
        klines = api.get_klines(symbols[0])
        print(f"Klines for {symbols[0]}: {klines[:5]}")
