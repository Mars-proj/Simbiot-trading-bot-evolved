from trading_bot.logging_setup import setup_logging
from trading_bot.utils.utils_utils import calculate_dynamic_threshold
import numpy as np

logger = setup_logging('mean_reversion_strategy')

class MeanReversionStrategy:
    def __init__(self, market_state: dict, lookback: int = 20, threshold: float = 2.0):
        self.volatility = market_state['volatility']
        self.lookback = lookback
        self.threshold = threshold

    def generate_signals(self, klines: list) -> list:
        """Generate trading signals using Mean Reversion strategy."""
        try:
            if len(klines) < self.lookback:
                logger.warning("Not enough kline data for Mean Reversion strategy")
                return []

            closes = [float(kline['close']) for kline in klines]
            
            signals = []
            for i in range(self.lookback - 1, len(klines)):
                window = closes[i - self.lookback + 1:i + 1]
                mean = np.mean(window)
                std = np.std(window)
                
                # Динамический порог на основе волатильности
                adjusted_threshold = self.threshold * (1 + self.volatility)
                price = closes[i]
                
                if price > mean + adjusted_threshold * std:
                    signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'sell'})
                elif price < mean - adjusted_threshold * std:
                    signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'buy'})
                else:
                    signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'hold'})
            
            logger.info(f"Generated {len(signals)} Mean Reversion signals")
            return signals
        except Exception as e:
            logger.error(f"Failed to generate Mean Reversion signals: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    strategy = MeanReversionStrategy(market_state)
    klines = [{'timestamp': i, 'close': float(50000 + i * 100)} for i in range(30)]
    signals = strategy.generate_signals(klines)
    print(f"Signals: {signals}")
