from trading_bot.logging_setup import setup_logging

logger = setup_logging('exchange_detector')

class ExchangeDetector:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.exchanges = {
            "binance": "BinanceAPI",
            "bitstamp": "BitstampAPI",
            "bybit": "BybitAPI",
            "coinbase": "CoinbaseAPI"
        }

    def detect_best_exchange(self, symbol: str) -> str:
        """Detect the best exchange for a given symbol based on market state."""
        try:
            best_exchange = "binance" if self.volatility < 0.5 else "coinbase"
            logger.info(f"Detected best exchange for {symbol}: {best_exchange}")
            return best_exchange
        except Exception as e:
            logger.error(f"Failed to detect best exchange for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    detector = ExchangeDetector(market_state)
    best_exchange = detector.detect_best_exchange("BTCUSDT")
    print(f"Best exchange: {best_exchange}")
