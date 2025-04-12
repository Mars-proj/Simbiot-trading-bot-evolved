import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_setup import setup_logging
from trading_bot.data_sources.market_data import MarketData
from trading_bot.strategies.strategy import Strategy
from trading_bot.analysis.volatility_analyzer import VolatilityAnalyzer

logger = setup_logging('macd_strategy')

class MACDStrategy(Strategy):
    def __init__(self, market_state: dict):
        super().__init__(market_state)
        self.short_period = 12
        self.long_period = 26
        self.signal_period = 9
        self.market_data = MarketData(market_state)
        self.volatility_analyzer = VolatilityAnalyzer(market_state)

    def calculate_ema(self, prices: list, period: int) -> list:
        """Calculate Exponential Moving Average."""
        if len(prices) < period:
            return [0] * len(prices)
        
        ema = []
        k = 2 / (period + 1)
        ema.append(sum(prices[:period]) / period)  # Первое значение — SMA
        
        for i in range(period, len(prices)):
            ema_value = (prices[i] * k) + (ema[-1] * (1 - k))
            ema.append(ema_value)
        
        return [0] * (period - 1) + ema

    def calculate_macd(self, closes: list) -> tuple:
        """Calculate MACD, Signal Line, and Histogram."""
        short_ema = self.calculate_ema(closes, self.short_period)
        long_ema = self.calculate_ema(closes, self.long_period)
        
        macd = [short - long for short, long in zip(short_ema, long_ema)]
        signal_line = self.calculate_ema(macd, self.signal_period)
        histogram = [m - s for m, s in zip(macd, signal_line)]
        
        return macd, signal_line, histogram

    async def generate_signal(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'mexc') -> str:
        """Generate a trading signal based on MACD strategy with dynamic thresholds."""
        try:
            # Получаем данные с биржи
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if len(klines) < self.long_period + self.signal_period:
                logger.warning(f"Not enough data for {symbol} to calculate MACD")
                return "hold"

            closes = [kline['close'] for kline in klines]
            macd, signal_line, histogram = self.calculate_macd(closes)

            # Динамически рассчитываем порог для сигнала на основе волатильности
            symbol_volatility = self.volatility_analyzer.analyze_volatility(symbol, exchange_name)
            signal_threshold = 0.0 + (symbol_volatility * 0.1)  # Порог корректируется на волатильность

            if macd[-1] > signal_line[-1] and histogram[-1] > signal_threshold:
                signal = "buy"
            elif macd[-1] < signal_line[-1] and histogram[-1] < -signal_threshold:
                signal = "sell"
            else:
                signal = "hold"

            logger.info(f"Generated signal for {symbol}: {signal} (MACD: {macd[-1]}, Signal: {signal_line[-1]}, Histogram: {histogram[-1]})")
            return signal
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    from trading_bot.symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    strategy = MACDStrategy(market_state)
    symbol_filter = SymbolFilter(market_state)
    
    # Получаем символы
    symbols = asyncio.run(strategy.market_data.get_symbols('mexc'))
    symbols = symbol_filter.filter_symbols(symbols, 'mexc')
    
    if symbols:
        signal = asyncio.run(strategy.generate_signal(symbols[0], '1h', 30, 'mexc'))
        print(f"Signal for {symbols[0]}: {signal}")
    else:
        print("No symbols available for testing")
