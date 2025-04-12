from trading_bot.logging_setup import setup_logging
from trading_bot.data_sources.market_data import MarketData
import numpy as np

logger = setup_logging('trend_analyzer')

class TrendAnalyzer:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.market_data = MarketData(market_state)

    def analyze_trend(self, symbol: str, exchange_name: str = 'binance') -> dict:
        """Analyze the price trend for a symbol."""
        try:
            # Получаем данные по символу
            klines = self.market_data.get_klines(symbol, '1h', 24, exchange_name)
            if not klines:
                logger.warning(f"No klines data for {symbol} on {exchange_name}")
                return {'status': 'failed', 'reason': 'no data'}

            # Извлекаем цены закрытия
            closes = np.array([kline['close'] for kline in klines])
            
            # Рассчитываем скользящую среднюю (SMA) для определения тренда
            window = 5
            sma = np.convolve(closes, np.ones(window)/window, mode='valid')
            trend_direction = 'up' if sma[-1] > sma[0] else 'down'

            # Динамическая корректировка интенсивности тренда на основе волатильности
            trend_strength = (sma[-1] - sma[0]) / sma[0] * (1 + self.volatility / 2) if sma[0] != 0 else 0.0

            analysis = {
                'trend': trend_direction,
                'trend_strength': trend_strength,
                'sma_last': sma[-1]
            }

            logger.info(f"Trend analysis for {symbol} on {exchange_name}: {analysis}")
            return analysis
        except Exception as e:
            logger.error(f"Failed to analyze trend for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    analyzer = TrendAnalyzer(market_state)
    symbols = analyzer.market_data.get_symbols('mexc')[:2]  # Первые 2 символа для теста с MEXC
    for symbol in symbols:
        analysis = analyzer.analyze_trend(symbol, 'mexc')
        print(f"Trend analysis for {symbol} on MEXC: {analysis}")
