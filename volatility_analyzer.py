import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_setup import setup_logging

logger = setup_logging('volatility_analyzer')

class VolatilityAnalyzer:
    def __init__(self, market_state: dict, market_data):
        self.market_state = market_state
        self.market_data = market_data
        self.volatility = market_state.get('volatility', 0.3)

    async def analyze_volatility(self, symbol: str, timeframe: str, limit: int, exchange_name: str) -> float:
        """Analyze the volatility of a symbol based on historical klines."""
        try:
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No klines data for {symbol} on {exchange_name}, returning default volatility")
                return self.volatility

            prices = [kline['close'] for kline in klines]
            if not prices or min(prices) == 0:
                logger.warning(f"Invalid price data for {symbol}, returning default volatility")
                return self.volatility

            volatility = (max(prices) - min(prices)) / min(prices)
            logger.info(f"Volatility for {symbol} on {exchange_name}: {volatility}")
            return volatility
        except Exception as e:
            logger.error(f"Failed to analyze volatility for {symbol}: {str(e)}")
            return self.volatility
