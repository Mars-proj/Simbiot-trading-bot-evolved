from trading_bot.logging_setup import setup_logging
from trading_bot.utils.utils_utils import calculate_dynamic_threshold
import numpy as np

logger = setup_logging('scalping_strategy')

class ScalpingStrategy:
    def __init__(self, market_state: dict, lookback: int = 5, profit_target: float = 0.005):
        self.volatility = market_state['volatility']
        self.lookback = lookback
        self.profit_target = profit_target

    def generate_signals(self, klines: list) -> list:
        """Generate trading signals using Scalping strategy."""
        try:
            if len(klines) < self.lookback:
                logger.warning("Not enough kline data for Scalping strategy")
                return []

            closes = [float(kline['close']) for kline in klines]
            
            signals = []
            for i in range(self.lookback - 1, len(klines)):
                window = closes[i - self.lookback + 1:i + 1]
                mean = np.mean(window)
                
                # Динамический целевой профит на основе волатильности
                adjusted_target = self.profit_target * (1 + self.volatility)
                price = closes[i]
                
                if price > mean * (1 + adjusted_target):
                    signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'sell'})
                elif price < mean * (1 - adjusted_target):
                    signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'buy'})
                else:
                    signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'hold'})
            
            logger.info(f"Generated {len(signals)} Scalping signals")
            return signals
        except Exception as e:
            logger.error(f"Failed to generate Scalping signals: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    strategy = ScalpingStrategy(market_state)
    klines = [{'timestamp': i, 'close': float(50000 + i * 100)} for i in range(10)]
    signals = strategy.generate_signals(klines)
    print(f"Signals: {signals}")
