import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
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
    def __init__(self, market_state: dict, market_data):
        self.volatility = market_state['volatility']
        self.market_data = market_data
        self.strategies = {
            'bollinger': BollingerStrategy(market_state, market_data=market_data),
            'rsi': RSIStrategy(market_state, market_data=market_data),
            'macd': MACDStrategy(market_state, market_data=market_data),
            'breakout': BreakoutStrategy(market_state, market_data=market_data),
            'grid': GridStrategy(market_state, market_data=market_data),
            'mean_reversion': MeanReversionStrategy(market_state, market_data=market_data),
            'ml': MLStrategy(market_state, market_data=market_data),
            'scalping': ScalpingStrategy(market_state, market_data=market_data),
            'trend': TrendStrategy(market_state, market_data=market_data),
            'volatility': VolatilityStrategy(market_state, market_data=market_data),
            'arbitrage': ArbitrageStrategy(market_state, market_data=market_data)
        }

    async def generate_signals(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'mexc') -> dict:
        """Generate signals for all strategies asynchronously."""
        try:
            signals = {}
            for strategy_name, strategy in self.strategies.items():
                signal = await strategy.generate_signal(symbol, timeframe, limit, exchange_name)
                signals[strategy_name] = signal
            logger.info(f"Generated signals: {signals}")
            return signals
        except Exception as e:
            logger.error(f"Failed to generate signals: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    import asyncio
    from data_sources.market_data import MarketData
    market_state = {'volatility': 0.3}
    market_data = MarketData(market_state)
    manager = StrategyManager(market_state, market_data=market_data)
    
    async def main():
        signals = await manager.generate_signals('BTC/USDT', '1h', 30, 'mexc')
        print(f"Signals: {signals}")
    
    asyncio.run(main())
