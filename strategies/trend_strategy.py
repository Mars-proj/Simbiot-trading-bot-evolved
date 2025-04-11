from trading_bot.logging_setup import setup_logging
from trading_bot.analysis.market_state_analyzer import MarketStateAnalyzer

logger = setup_logging('trend_strategy')

class TrendStrategy:
    def __init__(self, market_state: dict, lookback: int = 20):
        self.volatility = market_state['volatility']
        self.lookback = lookback
        self.analyzer = MarketStateAnalyzer(market_state)

    def generate_signals(self, klines: list) -> list:
        """Generate trading signals using Trend strategy."""
        try:
            if len(klines) < self.lookback:
                logger.warning("Not enough kline data for Trend strategy")
                return []

            # Анализируем состояние рынка
            state = self.analyzer.analyze_state(klines)
            trend = state['trend']
            
            signals = []
            for i in range(len(klines)):
                if trend == 'bullish':
                    signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'buy'})
                elif trend == 'bearish':
                    signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'sell'})
                else:
                    signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'hold'})
            
            logger.info(f"Generated {len(signals)} Trend signals")
            return signals
        except Exception as e:
            logger.error(f"Failed to generate Trend signals: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    strategy = TrendStrategy(market_state)
    klines = [{'timestamp': i, 'close': float(50000 + i * 100)} for i in range(30)]
    signals = strategy.generate_signals(klines)
    print(f"Signals: {signals}")
