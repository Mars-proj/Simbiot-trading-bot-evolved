import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_setup import setup_logging
from trading_bot.data_sources.market_data import MarketData

logger = setup_logging('volume_analyzer')

class VolumeAnalyzer:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.market_data = MarketData(market_state)

    async def analyze_volume(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'mexc') -> float:
        """Analyze trading volume for a symbol over a specified period."""
        try:
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No volume data for {symbol} on {exchange_name}")
                return 0.0

            total_volume = sum(float(kline['volume']) for kline in klines)
            logger.info(f"Total volume for {symbol} on {exchange_name} over {limit} periods: {total_volume}")
            return total_volume
        except Exception as e:
            logger.error(f"Failed to analyze volume for {symbol} on {exchange_name}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    analyzer = VolumeAnalyzer(market_state)
    
    async def main():
        volume = await analyzer.analyze_volume("BTC/USDT", "1h", 30, "mexc")
        print(f"Total volume for BTC/USDT on MEXC: {volume}")

    asyncio.run(main())
