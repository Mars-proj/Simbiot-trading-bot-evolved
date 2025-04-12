from typing import Dict
from trading_bot.strategies.bollinger_strategy import BollingerStrategy
from trading_bot.strategies.macd_strategy import MACDStrategy
from trading_bot.strategies.rsi_strategy import RSIStrategy
from trading_bot.strategies.signal_generator import SignalGenerator
from trading_bot.logging_setup import setup_logging
from trading_bot.data_sources.market_data import MarketData

logger = setup_logging('strategy_manager')

class StrategyManager:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.strategies: Dict[str, SignalGenerator] = {}
        self.market_data = MarketData(market_state)

    def add_strategy(self, strategy_name: str) -> None:
        """Add a strategy to the manager."""
        try:
            if strategy_name == "bollinger":
                strategy = BollingerStrategy({'volatility': self.volatility})
            elif strategy_name == "macd":
                strategy = MACDStrategy({'volatility': self.volatility})
            elif strategy_name == "rsi":
                strategy = RSIStrategy({'volatility': self.volatility})
            else:
                raise ValueError(f"Unsupported strategy: {strategy_name}")

            self.strategies[strategy_name] = SignalGenerator({'volatility': self.volatility}, strategy)
            logger.info(f"Added strategy: {strategy_name}")
        except Exception as e:
            logger.error(f"Failed to add strategy {strategy_name}: {str(e)}")
            raise

    def generate_signals(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'binance') -> Dict[str, list]:
        """Generate signals for all strategies."""
        try:
            signals = {}
            for name, generator in self.strategies.items():
                signals[name] = generator.generate_signals(symbol, timeframe, limit, exchange_name)
            logger.info(f"Generated signals for {symbol}: {signals}")
            return signals
        except Exception as e:
            logger.error(f"Failed to generate signals for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    from trading_bot.symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    manager = StrategyManager(market_state)
    symbol_filter = SymbolFilter(market_state)
    
    manager.add_strategy("bollinger")
    
    # Получаем символы
    symbols = symbol_filter.filter_symbols(manager.market_data.get_symbols('binance'), 'binance')
    
    if symbols:
        signals = manager.generate_signals(symbols[0], '1h', 30, 'binance')
        print(f"Signals for {symbols[0]}: {signals}")
    else:
        print("No symbols available for testing")
