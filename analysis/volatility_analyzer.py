import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from utils.logging_setup import setup_logging

logger = setup_logging('volatility_analyzer')

class VolatilityAnalyzer:
    def __init__(self, market_state: dict, market_data):
        self.volatility = market_state['volatility']
        self.market_data = market_data

    async def analyze_volatility(self, symbol: str, exchange_name: str = 'mexc') -> float:
        """Analyze the volatility of a symbol over a specified period."""
        try:
            klines = await self.market_data.get_klines(symbol, timeframe='1h', limit=30, exchange_name=exchange_name)
            if not klines:
                logger.warning(f"No data for {symbol} on {exchange_name}")
                return 0.0

            closes = [kline['close'] for kline in klines]
            returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
            volatility = (sum((r - sum(returns) / len(returns)) ** 2 for r in returns) / len(returns)) ** 0.5
            logger.info(f"Volatility for {symbol} on {exchange_name}: {volatility}")
            return volatility
        except Exception as e:
            logger.error(f"Failed to analyze volatility for {symbol} on {exchange_name}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    import asyncio
    from data_sources.market_data import MarketData
    from symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    market_data = MarketData(market_state)
    analyzer = VolatilityAnalyzer(market_state, market_data=market_data)
    
    async def main():
        symbol_filter = SymbolFilter(market_state, market_data=market_data)
        symbols = await market_data.get_symbols('mexc')
        symbols = await symbol_filter.filter_symbols(symbols, 'mexc')
        if symbols:
            volatility = await analyzer.analyze_volatility(symbols[0], 'mexc')
            print(f"Volatility for {symbols[0]} on MEXC: {volatility}")
        else:
            print("No symbols available for testing")

    asyncio.run(main())
