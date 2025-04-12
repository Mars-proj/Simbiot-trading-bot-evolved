from trading_bot.logging_setup import setup_logging
from .market_data import MarketData

logger = setup_logging('volume_analyzer')

class VolumeAnalyzer:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.market_data = MarketData(market_state)

    def analyze_volume(self, symbol: str, exchange_name: str = 'binance') -> float:
        """Analyze the trading volume of a symbol."""
        try:
            klines = self.market_data.get_klines(symbol, '1h', 24, exchange_name)  # Последние 24 часа
            if not klines:
                logger.warning(f"No volume data for {symbol} on {exchange_name}")
                return 0.0

            total_volume = sum(kline['volume'] for kline in klines)
            
            # Динамическая корректировка на основе волатильности
            adjusted_volume = total_volume * (1 - self.volatility / 2)
            
            logger.info(f"Volume for {symbol} on {exchange_name}: {adjusted_volume}")
            return adjusted_volume
        except Exception as e:
            logger.error(f"Failed to analyze volume for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    analyzer = VolumeAnalyzer(market_state)
    symbols = analyzer.market_data.get_symbols('binance')[:2]  # Первые 2 символа для теста
    for symbol in symbols:
        volume = analyzer.analyze_volume(symbol)
        print(f"Volume for {symbol}: {volume}")
