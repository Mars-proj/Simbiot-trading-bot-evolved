from trading_bot.logging_setup import setup_logging
from trading_bot.data_sources.market_data import MarketData
import numpy as np

logger = setup_logging('volatility_analyzer')

class VolatilityAnalyzer:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.market_data = MarketData(market_state)

    def analyze_volatility(self, symbol: str, exchange_name: str = 'binance') -> float:
        """Analyze the volatility of a symbol on the specified exchange."""
        try:
            # Получаем данные по ценам закрытия за последние 24 часа
            klines = self.market_data.get_klines(symbol, '1h', 24, exchange_name)
            if not klines:
                logger.warning(f"No klines data for {symbol} on {exchange_name}")
                return 0.0

            # Рассчитываем логарифмические доходности
            closes = [kline['close'] for kline in klines]
            returns = np.diff(np.log(closes))
            
            # Рассчитываем волатильность как стандартное отклонение доходностей
            symbol_volatility = np.std(returns) if len(returns) > 1 else 0.0

            logger.info(f"Volatility for {symbol} on {exchange_name}: {symbol_volatility}")
            return symbol_volatility
        except Exception as e:
            logger.error(f"Failed to analyze volatility for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    analyzer = VolatilityAnalyzer(market_state)
    symbols = analyzer.market_data.get_symbols('mexc')[:2]  # Первые 2 символа для теста с MEXC
    for symbol in symbols:
        volatility = analyzer.analyze_volatility(symbol, 'mexc')
        print(f"Volatility for {symbol} on MEXC: {volatility}")
