from trading_bot.logging_setup import setup_logging
from trading_bot.utils.utils_utils import calculate_dynamic_threshold
import numpy as np

logger = setup_logging('breakout_strategy')

class BreakoutStrategy:
    def __init__(self, market_state: dict, lookback: int = 20):
        self.volatility = market_state['volatility']
        self.lookback = lookback

    def generate_signals(self, klines: list) -> list:
        """Generate trading signals using Breakout strategy."""
        try:
            if len(klines) < self.lookback:
                logger.warning("Not enough kline data for Breakout strategy")
                return []

            highs = [float(kline['high']) for kline in klines]
            lows = [float(kline['low']) for kline in klines]
            closes = [float(kline['close']) for kline in klines]
            
            signals = []
            for i in range(self.lookback - 1, len(klines)):
                # Рассчитываем максимум и минимум за lookback период
                window_highs = highs[i - self.lookback + 1:i + 1]
                window_lows = lows[i - self.lookback + 1:i + 1]
                
                # Динамический порог на основе волатильности
                breakout_threshold = calculate_dynamic_threshold({'volatility': self.volatility}, 1.0)
                resistance = max(window_highs) * (1 + breakout_threshold)
                support = min(window_lows) * (1 - breakout_threshold)
                
                price = closes[i]
                if price > resistance:
                    signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'buy'})
                elif price < support:
                    signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'sell'})
                else:
                    signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'hold'})
            
            logger.info(f"Generated {len(signals)} Breakout signals")
            return signals
        except Exception as e:
            logger.error(f"Failed to generate Breakout signals: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    strategy = BreakoutStrategy(market_state)
    klines = [{'timestamp': i, 'high': float(51000 + i * 100), 'low': float(49000 + i * 100), 'close': float(50000 + i * 100)} for i in range(30)]
    signals = strategy.generate_signals(klines)
    print(f"Signals: {signals}")
