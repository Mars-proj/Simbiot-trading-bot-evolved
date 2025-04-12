from trading_bot.logging_setup import setup_logging
from trading_bot.data_sources.market_data import MarketData
import numpy as np

logger = setup_logging('price_analyzer')

class PriceAnalyzer:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.market_data = MarketData(market_state)

    def analyze_price(self, symbol: str, exchange_name: str = 'binance') -> dict:
        """Analyze price trends for a symbol."""
        try:
            # Получаем данные по символу
            klines = self.market_data.get_klines(symbol, '1h', 24, exchange_name)
            if not klines:
                logger.warning(f"No klines data for {symbol} on {exchange_name}")
                return {'status': 'failed', 'reason': 'no data'}

            # Извлекаем цены закрытия
            closes = [kline['close'] for kline in klines]
            
            # Рассчитываем среднюю цену и тренд
            avg_price = sum(closes) / len(closes)
            price_change = (closes[-1] - closes[0]) / closes[0] if closes[0] != 0 else 0.0

            # Динамическая корректировка на основе волатильности
            adjusted_change = price_change * (1 + self.volatility / 2)

            analysis = {
                'average_price': avg_price,
                'price_change': adjusted_change,
                'trend': 'up' if price_change > 0 else 'down'
            }

            logger.info(f"Price analysis for {symbol} on {exchange_name}: {analysis}")
            return analysis
        except Exception as e:
            logger.error(f"Failed to analyze price for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    analyzer = PriceAnalyzer(market_state)
    symbols = analyzer.market_data.get_symbols('mexc')[:2]  # Первые 2 символа для теста с MEXC
    for symbol in symbols:
        analysis = analyzer.analyze_price(symbol, 'mexc')
        print(f"Price analysis for {symbol} on MEXC: {analysis}")
