from trading_bot.logging_setup import setup_logging
from trading_bot.analysis.volatility_analyzer import VolatilityAnalyzer

logger = setup_logging('volatility_strategy')

class VolatilityStrategy:
    def __init__(self, market_state: dict, volatility_threshold: float = 0.5):
        self.volatility = market_state['volatility']
        self.volatility_threshold = volatility_threshold
        self.analyzer = VolatilityAnalyzer(market_state)

    def generate_signals(self, klines: list) -> list:
        """Generate trading signals using Volatility strategy."""
        try:
            if len(klines) < 2:
                logger.warning("Not enough kline data for Volatility strategy")
                return []

            # Анализируем волатильность
            volatility = self.analyzer.analyze_volatility(klines)
            
            # Динамический порог на основе текущей волатильности
            adjusted_threshold = self.volatility_threshold * (1 + self.volatility)
            
            signals = []
            for i in range(len(klines)):
                if volatility > adjusted_threshold:
                    signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'hold'})
                else:
                    signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'buy'})
            
            logger.info(f"Generated {len(signals)} Volatility signals")
            return signals
        except Exception as e:
            logger.error(f"Failed to generate Volatility signals: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    strategy = VolatilityStrategy(market_state)
    klines = [{'timestamp': i, 'close': float(50000 + i * 100)} for i in range(10)]
    signals = strategy.generate_signals(klines)
    print(f"Signals: {signals}")
