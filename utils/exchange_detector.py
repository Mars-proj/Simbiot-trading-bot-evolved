import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from .logging_setup import setup_logging

logger = setup_logging('exchange_detector')

class ExchangeDetector:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.exchanges = ['binance', 'kraken', 'mexc', 'bitstamp', 'bybit', 'coinbase', 'huobi', 'kucoin']

    def detect_exchange(self, symbol: str) -> str:
        """Detect the exchange for a given symbol (simplified)."""
        try:
            # Симулируем определение биржи
            exchange = self.exchanges[hash(symbol) % len(self.exchanges)]
            logger.info(f"Detected exchange for {symbol}: {exchange}")
            return exchange
        except Exception as e:
            logger.error(f"Failed to detect exchange for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    detector = ExchangeDetector(market_state)
    exchange = detector.detect_exchange("BTC/USDT")
    print(f"Detected exchange: {exchange}")
