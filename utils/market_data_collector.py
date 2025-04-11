from trading_bot.logging_setup import setup_logging
from trading_bot.utils.cache_manager import CacheManager
from .binance_api import BinanceAPI
from .bitstamp_api import BitstampAPI
from .bybit_api import BybitAPI
from .coinbase_api import CoinbaseAPI
from .huobi_api import HuobiAPI
from .kraken_api import KrakenAPI
from .kucoin_api import KucoinAPI
from .exchange_detector import ExchangeDetector

logger = setup_logging('market_data_collector')

class MarketDataCollector:
    def __init__(self, market_state: dict):
        self.cache = CacheManager(market_state)
        self.detector = ExchangeDetector(market_state)
        self.exchanges = {
            "binance": BinanceAPI("your_api_key", "your_api_secret", market_state),
            "bitstamp": BitstampAPI(market_state),
            "bybit": BybitAPI("your_api_key", "your_api_secret", market_state),
            "coinbase": CoinbaseAPI("your_api_key", "your_api_secret", market_state),
            "huobi": HuobiAPI("your_api_key", "your_api_secret", market_state),
            "kraken": KrakenAPI("your_api_key", "your_api_secret", market_state),
            "kucoin": KucoinAPI("your_api_key", "your_api_secret", market_state)
        }

    def collect_klines(self, symbol: str, interval: str) -> list:
        """Collect kline data from the best exchange."""
        try:
            cache_key = f"klines_{symbol}_{interval}"
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return cached_data

            exchange_name = self.detector.detect_best_exchange(symbol)
            exchange = self.exchanges[exchange_name]

            if exchange_name == "binance":
                response = exchange.get_klines(symbol, interval)
            elif exchange_name == "bitstamp":
                response = exchange.get_ohlc(symbol.replace("/", ""), step=3600)
            elif exchange_name == "bybit":
                response = exchange.get_kline(symbol, interval)
            elif exchange_name == "coinbase":
                response = exchange.get_candles(symbol.replace("/", "-"))
            elif exchange_name == "huobi":
                response = exchange.get_kline(symbol.lower(), interval)
            elif exchange_name == "kraken":
                response = exchange.get_ohlc(symbol.replace("/", ""))
            elif exchange_name == "kucoin":
                response = exchange.get_kline(symbol, interval)
            else:
                raise ValueError(f"Unsupported exchange: {exchange_name}")

            klines = response.json()
            self.cache.set(cache_key, klines)
            logger.info(f"Collected klines for {symbol} from {exchange_name}")
            return klines
        except Exception as e:
            logger.error(f"Failed to collect klines for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    collector = MarketDataCollector(market_state)
    klines = collector.collect_klines("BTCUSDT", "1h")
    print(f"Klines: {klines}")
