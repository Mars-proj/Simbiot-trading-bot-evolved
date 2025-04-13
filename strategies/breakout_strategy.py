import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from utils.logging_setup import setup_logging
from .strategy import Strategy
from analysis.volatility_analyzer import VolatilityAnalyzer

logger = setup_logging('breakout_strategy')

class BreakoutStrategy(Strategy):
    def __init__(self, market_state: dict, market_data):
        super().__init__(market_state)
        self.lookback_period = 20
        self.market_data = market_data
        self.volatility_analyzer = VolatilityAnalyzer(market_state, market_data=market_data)

    async def generate_signal(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'mexc') -> str:
        """Generate a trading signal based on breakout strategy with dynamic thresholds."""
        try:
            # Получаем данные с биржи
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if len(klines) < self.lookback_period:
                logger.warning(f"Not enough data for {symbol} to calculate breakout levels")
                return "hold"

            # Calculate high and low over the lookback period
            highs = [kline['high'] for kline in klines[-self.lookback_period:]]
            lows = [kline['low'] for kline in klines[-self.lookback_period:]]
            
            # Динамически рассчитываем порог breakout на основе волатильности
            symbol_volatility = self.volatility_analyzer.analyze_volatility(symbol, exchange_name)
            breakout_threshold = 1.02 + (symbol_volatility * 0.05)  # Базовый порог 2%, корректируется на волатильность

            breakout_high = max(highs) * breakout_threshold
            breakout_low = min(lows) / breakout_threshold

            price = klines[-1]['close']
            if price > breakout_high:
                signal = "buy"
            elif price < breakout_low:
                signal = "sell"
            else:
                signal = "hold"

            logger.info(f"Generated signal for {symbol}: {signal} (Price: {price}, Breakout High: {breakout_high}, Breakout Low: {breakout_low})")
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
    strategy = BreakoutStrategy(market_state, market_data=market_data)
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
