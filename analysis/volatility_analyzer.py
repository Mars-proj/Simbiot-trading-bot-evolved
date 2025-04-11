from trading_bot.logging_setup import setup_logging
from trading_bot.data_sources.data_utils import calculate_volatility

logger = setup_logging('volatility_analyzer')

class VolatilityAnalyzer:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']

    def analyze_volatility(self, klines: list) -> float:
        """Analyze volatility of market data."""
        try:
            if not klines:
                logger.warning("No kline data provided")
                return 0.0

            # Рассчитываем волатильность
            volatility = calculate_volatility(klines)
            
            # Корректируем волатильность на основе market_state
            adjusted_volatility = volatility * (1 + self.volatility / 2)
            
            logger.info(f"Analyzed volatility: {adjusted_volatility}")
            return adjusted_volatility
        except Exception as e:
            logger.error(f"Failed to analyze volatility: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    analyzer = VolatilityAnalyzer(market_state)
    klines = [{'close': float(50000 + i * 100)} for i in range(10)]
    volatility = analyzer.analyze_volatility(klines)
    print(f"Volatility: {volatility}")
