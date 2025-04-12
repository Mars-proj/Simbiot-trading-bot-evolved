import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_setup import setup_logging
from data_sources.market_data import MarketData
from .strategy import Strategy
from analysis.volatility_analyzer import VolatilityAnalyzer

logger = setup_logging('trend_strategy')

class TrendStrategy(Strategy):
    def __init__(self, market_state: dict):
        super().__init__(market_state)
        self.lookback_period = 20
        self.market_data = MarketData(market_state)
        self.volatility_analyzer = VolatilityAnalyzer(market_state)

    async def generate_signal(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'mexc') -> str:
        """Generate a trading signal based on trend strategy with dynamic thresholds."""
        try:
            # Получаем данные с биржи
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if len(klines) < self.lookback_period:
                logger.warning(f"Not enough data for {symbol} to calculate trend")
                return "hold"

            closes = [kline['close'] for kline in klines[-self.lookback_period:]]
            
            # Динамически рассчитываем периоды MA на основе волатильности
            symbol_volatility = self.volatility_analyzer.analyze_volatility(symbol, exchange_name)
            short_period = int(5 * (1 - symbol_volatility * 0.5))  # Базовый период 5, уменьшается при высокой волатильности
            long_period = int(self.lookback_period * (1 + symbol_volatility * 0.5))  # Базовый период 20, увеличивается при высокой волатильности
            short_period = max(3, short_period)  # Минимальный период 3
            long_period = min(50, long_period)   # Максимальный период 50

            # Simple trend detection using moving average
            ma_short = sum(closes[-short_period:]) / short_period
            ma_long = sum(closes[-long_period:]) / long_period

            if ma_short > ma_long:
                signal = "buy"
            elif ma_short < ma_long:
                signal = "sell"
            else:
                signal = "hold"

            logger.info(f"Generated signal for {symbol}: {signal} (MA Short: {ma_short}, MA Long: {ma_long})")
            return signal
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    from symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    strategy = TrendStrategy(market_state)
    symbol_filter = SymbolFilter(market_state)
    
    # Получаем символы
    symbols = asyncio.run(strategy.market_data.get_symbols('mexc'))
    symbols = symbol_filter.filter_symbols(symbols, 'mexc')
    
    if symbols:
        signal = asyncio.run(strategy.generate_signal(symbols[0], '1h', 30, 'mexc'))
        print(f"Signal for {symbols[0]}: {signal}")
    else:
        print("No symbols available for testing")
