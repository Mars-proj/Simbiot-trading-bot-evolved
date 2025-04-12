import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from .bollinger_strategy import BollingerStrategy
from .rsi_strategy import RSIStrategy
from .macd_strategy import MACDStrategy
from .breakout_strategy import BreakoutStrategy
from .grid_strategy import GridStrategy
from .mean_reversion_strategy import MeanReversionStrategy
from .ml_strategy import MLStrategy
from .scalping_strategy import ScalpingStrategy
from .trend_strategy import TrendStrategy
from .volatility_strategy import VolatilityStrategy
from .arbitrage_strategy import ArbitrageStrategy
from utils.logging_setup import setup_logging

logger = setup_logging('strategy_manager')

class StrategyManager:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.strategies = {
            'bollinger': BollingerStrategy(market_state),
            'rsi': RSIStrategy(market_state),
            'macd': MACDStrategy(market_state),
            'breakout': BreakoutStrategy(market_state),
            'grid': GridStrategy(market_state),
            'mean_reversion': MeanReversionStrategy(market_state),
            'ml': MLStrategy(market_state),
            'scalping': ScalpingStrategy(market_state),
            'trend': TrendStrategy(market_state),
            'volatility': VolatilityStrategy(market_state),
            'arbitrage': ArbitrageStrategy(market_state)
        }

    def generate_signals(self, klines: list) -> dict:
        """Generate signals for all strategies."""
        try:
            signals = {}
            for strategy_name, strategy in self.strategies.items():
                signal = strategy.generate_signal(klines)
                signals[strategy_name] = signal
            logger.info(f"Generated signals: {signals}")
            return signals
        except Exception as e:
            logger.error(f"Failed to generate signals: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    manager = StrategyManager(market_state)
    klines = [{'close': i} for i in range(1, 31)]  # Симулируем данные
    signals = manager.generate_signals(klines)
    print(f"Signals: {signals}")
