from trading_bot.logging_setup import setup_logging
from trading_bot.data_sources.market_data import MarketData

logger = setup_logging('market_analyzer')

class MarketAnalyzer:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.market_data = MarketData(market_state)

    def analyze_market(self, symbol: str, exchange_name: str = 'binance') -> dict:
        """Analyze market conditions for a symbol."""
        try:
            # Получаем данные по символу
            klines = self.market_data.get_klines(symbol, '1h', 24, exchange_name)
            if not klines:
                logger.warning(f"No klines data for {symbol} on {exchange_name}")
                return {'status': 'failed', 'reason': 'no data'}

            # Рассчитываем основные метрики
            closes = [kline['close'] for kline in klines]
            avg_price = sum(closes) / len(closes)
            high = max(kline['high'] for kline in klines)
            low = min(kline['low'] for kline in klines)

            # Динамическая корректировка на основе волатильности
            adjusted_range = (high - low) * (1 + self.volatility / 2)

            analysis = {
                'average_price': avg_price,
                'price_range': adjusted_range,
                'high': high,
                'low': low
            }

            logger.info(f"Market analysis for {symbol} on {exchange_name}: {analysis}")
            return analysis
        except Exception as e:
            logger.error(f"Failed to analyze market for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    analyzer = MarketAnalyzer(market_state)
    symbols = analyzer.market_data.get_symbols('mexc')[:2]  # Первые 2 символа для теста с MEXC
    for symbol in symbols:
        analysis = analyzer.analyze_market(symbol, 'mexc')
        print(f"Market analysis for {symbol} on MEXC: {analysis}")
