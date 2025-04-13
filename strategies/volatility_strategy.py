import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from utils.logging_setup import setup_logging
from .strategy import Strategy
from analysis.volatility_analyzer import VolatilityAnalyzer

logger = setup_logging('volatility_strategy')

class VolatilityStrategy(Strategy):
    def __init__(self, market_state: dict, market_data):
        super().__init__(market_state)
        self.lookback_period = 20
        self.market_data = market_data
        self.volatility_analyzer = VolatilityAnalyzer(market_state, market_data=market_data)

    async def generate_signal(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'mexc') -> str:
        """Generate a trading signal based on volatility strategy with dynamic thresholds."""
        try:
            # Получаем данные с биржи
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if len(klines) < self.lookback_period:
                logger.warning(f"Not enough data for {symbol} to calculate volatility")
                return "hold"

            closes = [kline['close'] for kline in klines[-self.lookback_period:]]
            returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
            volatility = (sum((r - sum(returns) / len(returns)) ** 2 for r in returns) / len(returns)) ** 0.5

            # Динамически рассчитываем порог на основе рыночной волатильности
            symbol_volatility = self.volatility_analyzer.analyze_volatility(symbol, exchange_name)
            volatility_threshold = 0.03 * (1 + symbol_volatility)  # Базовый порог 3%, корректируется на волатильность

            if volatility > volatility_threshold:
                signal = "sell"  # High volatility, exit position
            else:
                signal = "buy"  # Low volatility, enter position

            logger.info(f"Generated signal for {symbol}: {signal} (Volatility: {volatility}, Threshold: {volatility_threshold})")
            return signal
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    import asyncio
    from data_sources.market_data import MarketData
    from symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    market_data = MarketData(market_state)
    strategy = VolatilityStrategy(market_state, market_data=market_data)
    symbol_filter = SymbolFilter(market_state, market_data=market_data)
    
    async def main():
        symbols = await strategy.market_data.get_symbols('mexc')
        symbols = await symbol_filter.filter_symbols(symbols, 'mexc')
        
        if symbols:
            signal = await strategy.generate_signal(symbols[0], '1h', 30, 'mexc')
            print(f"Signal for {symbols[0]}: {signal}")
        else:
            print("No symbols available for testing")

    asyncio.run(main())
