import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_setup import setup_logging
from data_sources.market_data import MarketData
from .strategy import Strategy
from analysis.volatility_analyzer import VolatilityAnalyzer
import statistics

logger = setup_logging('bollinger_strategy')

class BollingerStrategy(Strategy):
    def __init__(self, market_state: dict):
        super().__init__(market_state)
        self.bollinger_period = 20
        self.market_data = MarketData(market_state)
        self.volatility_analyzer = VolatilityAnalyzer(market_state)

    def calculate_bollinger_bands(self, closes: list, symbol: str, exchange_name: str) -> tuple:
        """Calculate Bollinger Bands with dynamic standard deviation multiplier."""
        if len(closes) < self.bollinger_period:
            return None, None, None

        sma = sum(closes[-self.bollinger_period:]) / self.bollinger_period
        std_dev = statistics.stdev(closes[-self.bollinger_period:])

        # Динамически рассчитываем множитель стандартного отклонения на основе волатильности
        symbol_volatility = self.volatility_analyzer.analyze_volatility(symbol, exchange_name)
        std_dev_multiplier = 2 * (1 + symbol_volatility)  # Базовый множитель 2, корректируется на волатильность

        upper_band = sma + (std_dev * std_dev_multiplier)
        lower_band = sma - (std_dev * std_dev_multiplier)
        return sma, upper_band, lower_band

    async def generate_signal(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'mexc') -> str:
        """Generate a trading signal based on Bollinger Bands with dynamic thresholds."""
        try:
            # Получаем данные с биржи
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if len(klines) < self.bollinger_period:
                logger.warning(f"Not enough data for {symbol} to calculate Bollinger Bands")
                return "hold"

            closes = [kline['close'] for kline in klines]
            sma, upper_band, lower_band = self.calculate_bollinger_bands(closes, symbol, exchange_name)

            if sma is None:
                return "hold"

            current_price = closes[-1]
            if current_price > upper_band:
                signal = "sell"
            elif current_price < lower_band:
                signal = "buy"
            else:
                signal = "hold"

            logger.info(f"Generated signal for {symbol}: {signal} (Price: {current_price}, SMA: {sma}, Upper: {upper_band}, Lower: {lower_band})")
            return signal
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    from symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    strategy = BollingerStrategy(market_state)
    symbol_filter = SymbolFilter(market_state)
    
    # Получаем символы
    symbols = asyncio.run(strategy.market_data.get_symbols('mexc'))
    symbols = symbol_filter.filter_symbols(symbols, 'mexc')
    
    if symbols:
        signal = asyncio.run(strategy.generate_signal(symbols[0], '1h', 30, 'mexc'))
        print(f"Signal for {symbols[0]}: {signal}")
    else:
        print("No symbols available for testing")
