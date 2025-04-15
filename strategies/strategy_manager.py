from utils.logging_setup import setup_logging
from .bollinger_strategy import BollingerStrategy
from .rsi_strategy import RSIStrategy
from .macd_strategy import MACDStrategy
from .ml_strategy import MLStrategy
from .arbitrage_strategy import ArbitrageStrategy
from .mean_reversion_strategy import MeanReversionStrategy
from .grid_strategy import GridStrategy
from .breakout_strategy import BreakoutStrategy
from .scalping_strategy import ScalpingStrategy
from .trend_strategy import TrendStrategy
from .volatility_strategy import VolatilityStrategy
from .signal_generator import SignalGenerator

logger = setup_logging('strategy_manager')

class StrategyManager:
    def __init__(self, market_state, market_data, volatility_analyzer, online_learning):
        self.market_state = market_state
        self.market_data = market_data
        self.volatility_analyzer = volatility_analyzer
        self.online_learning = online_learning
        self.strategies = [
            BollingerStrategy(market_state, market_data, volatility_analyzer),
            RSIStrategy(market_state, market_data, volatility_analyzer),
            MACDStrategy(market_state, market_data, volatility_analyzer),
            MLStrategy(market_state, market_data, volatility_analyzer, self.online_learning),
            ArbitrageStrategy(market_state, market_data, volatility_analyzer),
            MeanReversionStrategy(market_state, market_data, volatility_analyzer),
            GridStrategy(market_state, market_data, volatility_analyzer),
            BreakoutStrategy(market_state, market_data, volatility_analyzer),
            ScalpingStrategy(market_state, market_data, volatility_analyzer),
            TrendStrategy(market_state, market_data, volatility_analyzer),
            VolatilityStrategy(market_state, market_data, volatility_analyzer),
            SignalGenerator(market_state, market_data, volatility_analyzer)
        ]

    async def generate_signals(self, symbol, klines, prediction):
        """Generate signals from all strategies asynchronously."""
        try:
            signals = []
            for strategy in self.strategies:
                signal = await strategy.generate_signal(symbol, klines, "1m", 200, "mexc")
                if signal:
                    signals.append(signal)
            logger.info(f"Generated signals for {symbol}: {signals}")
            return signals
        except Exception as e:
            logger.error(f"Failed to generate signals for {symbol}: {str(e)}")
            return []
