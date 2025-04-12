import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_setup import setup_logging
from data_sources.market_data import MarketData
from .strategy import Strategy
from analysis.volatility_analyzer import VolatilityAnalyzer

logger = setup_logging('grid_strategy')

class GridStrategy(Strategy):
    def __init__(self, market_state: dict):
        super().__init__(market_state)
        self.grid_levels = 5
        self.market_data = MarketData(market_state)
        self.volatility_analyzer = VolatilityAnalyzer(market_state)

    async def generate_signal(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'mexc') -> str:
        """Generate a trading signal based on grid strategy with dynamic spacing."""
        try:
            # Получаем данные с биржи
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if len(klines) < 1:
                logger.warning(f"No data for {symbol} to calculate grid levels")
                return "hold"

            # Динамически рассчитываем grid spacing на основе волатильности
            symbol_volatility = self.volatility_analyzer.analyze_volatility(symbol, exchange_name)
            grid_spacing = 0.01 * (1 + symbol_volatility)  # Базовый spacing 1%, корректируется на волатильность

            # Calculate grid levels based on the last price
            last_price = klines[-1]['close']
            grid_base = last_price * (1 - self.grid_levels * grid_spacing / 2)
            grid_levels = [grid_base + i * grid_spacing * last_price for i in range(self.grid_levels)]

            # Find the closest grid level
            price = klines[-1]['close']
            closest_level = min(grid_levels, key=lambda x: abs(x - price))
            
            if price > closest_level:
                signal = "buy"
            elif price < closest_level:
                signal = "sell"
            else:
                signal = "hold"

            logger.info(f"Generated signal for {symbol}: {signal} (Price: {price}, Closest Level: {closest_level})")
            return signal
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    from symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    strategy = GridStrategy(market_state)
    symbol_filter = SymbolFilter(market_state)
    
    # Получаем символы
    symbols = asyncio.run(strategy.market_data.get_symbols('mexc'))
    symbols = symbol_filter.filter_symbols(symbols, 'mexc')
    
    if symbols:
        signal = asyncio.run(strategy.generate_signal(symbols[0], '1h', 30, 'mexc'))
        print(f"Signal for {symbols[0]}: {signal}")
    else:
        print("No symbols available for testing")
