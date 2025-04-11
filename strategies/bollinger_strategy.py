from trading_bot.logging_setup import setup_logging
from trading_bot.utils.utils_utils import calculate_dynamic_threshold
import numpy as np

logger = setup_logging('bollinger_strategy')

class BollingerStrategy:
    def __init__(self, market_state: dict, period: int = 20, std_dev: float = 2.0):
        self.volatility = market_state['volatility']
        self.period = period
        self.std_dev = std_dev

    def generate_signals(self, klines: list) -> list:
        """Generate trading signals using Bollinger Bands."""
        try:
            if len(klines) < self.period:
                logger.warning("Not enough kline data for Bollinger Bands")
                return []

            closes = [float(kline['close']) for kline in klines]
            
            signals = []
            for i in range(self.period - 1, len(closes)):
                window = closes[i - self.period + 1:i + 1]
                sma = np.mean(window)
                std = np.std(window)
                
                # Динамические границы на основе волатильности
                upper_band = sma + self.std_dev * std * (1 + self.volatility)
                lower_band = sma - self.std_dev * std * (1 + self.volatility)
                
                price = closes[i]
                if price > upper_band:
                    signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'sell'})
                elif price < lower_band:
                    signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'buy'})
                else:
                    signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'hold'})
            
            logger.info(f"Generated {len(signals)} Bollinger Band signals")
            return signals
        except Exception as e:
            logger.error(f"Failed to generate Bollinger Band signals: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    strategy = BollingerStrategy(market_state)
    klines = [{'timestamp': i, 'close': float(50000 + i * 100)} for i in range(30)]
    signals = strategy.generate_signals(klines)
    print(f"Signals: {signals}")
