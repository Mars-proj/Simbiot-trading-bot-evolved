from trading_bot.logging_setup import setup_logging
import numpy as np

logger = setup_logging('correlation_analyzer')

class CorrelationAnalyzer:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']

    def calculate_correlation(self, data1: list, data2: list) -> float:
        """Calculate correlation between two datasets."""
        try:
            if len(data1) != len(data2) or not data1 or not data2:
                logger.warning("Datasets must be of equal length and non-empty")
                return 0.0

            values1 = [float(d['close']) for d in data1]
            values2 = [float(d['close']) for d in data2]
            
            # Динамическая корректировка на основе волатильности
            if self.volatility > 0.5:
                logger.info("High volatility detected, adjusting correlation calculation")
                values1 = [v * (1 - self.volatility) for v in values1]
                values2 = [v * (1 - self.volatility) for v in values2]

            correlation = np.corrcoef(values1, values2)[0, 1]
            logger.info(f"Calculated correlation: {correlation}")
            return correlation
        except Exception as e:
            logger.error(f"Failed to calculate correlation: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    analyzer = CorrelationAnalyzer(market_state)
    data1 = [
        {'close': 50000},
        {'close': 51000},
        {'close': 52000},
        {'close': 53000}
    ]
    data2 = [
        {'close': 60000},
        {'close': 61000},
        {'close': 62000},
        {'close': 63000}
    ]
    correlation = analyzer.calculate_correlation(data1, data2)
    print(f"Correlation: {correlation}")
