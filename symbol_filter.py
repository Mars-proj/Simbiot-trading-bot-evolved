import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from utils.logging_setup import setup_logging
from trading_bot.data_sources.market_data import MarketData

logger = setup_logging('symbol_filter')

class SymbolFilter:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.filters = {}
        self.market_data = MarketData(market_state)

    def setup_default_filters(self, min_liquidity: float = 1000000, max_volatility: float = 0.5) -> None:
        """Set up default filters for symbol selection."""
        self.filters['min_liquidity'] = min_liquidity
        self.filters['max_volatility'] = max_volatility
        logger.info(f"Set up default filters: {self.filters}")

    def filter_symbols(self, symbols: list, exchange_name: str) -> list:
        """Filter symbols based on liquidity and volatility."""
        try:
            filtered_symbols = []
            for symbol in symbols:
                try:
                    # Получаем данные для символа
                    klines = self.market_data.get_klines(symbol, '1h', 30, exchange_name)
                    if not klines:
                        logger.warning(f"No klines data for {symbol} on {exchange_name}, skipping")
                        continue

                    # Проверяем ликвидность (объём торгов)
                    total_volume = sum(float(kline['volume']) for kline in klines)
                    if total_volume < self.filters['min_liquidity']:
                        logger.debug(f"Symbol {symbol} filtered out due to low liquidity: {total_volume}")
                        continue

                    # Проверяем волатильность
                    closes = [float(kline['close']) for kline in klines]
                    returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
                    volatility = (sum((r - sum(returns) / len(returns)) ** 2 for r in returns) / len(returns)) ** 0.5
                    if volatility > self.filters['max_volatility']:
                        logger.debug(f"Symbol {symbol} filtered out due to high volatility: {volatility}")
                        continue

                    filtered_symbols.append(symbol)
                except Exception as e:
                    logger.warning(f"Skipping {symbol} due to error: {str(e)}")
                    continue

            logger.info(f"Filtered {len(filtered_symbols)} symbols: {filtered_symbols}")
            return filtered_symbols
        except Exception as e:
            logger.error(f"Failed to filter symbols: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    symbol_filter = SymbolFilter(market_state)
    symbols = ['BTC/USDT', 'ETH/USDT', 'XRP/USDT']
    filtered = symbol_filter.filter_symbols(symbols, 'mexc')
    print(f"Filtered symbols: {filtered}")
