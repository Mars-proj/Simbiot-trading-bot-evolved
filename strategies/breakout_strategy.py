from trading_bot.logging_setup import setup_logging
from trading_bot.data_sources.market_data import MarketData
from trading_bot.strategies.strategy import Strategy
from trading_bot.analysis.volatility_analyzer import VolatilityAnalyzer

logger = setup_logging('breakout_strategy')

class BreakoutStrategy(Strategy):
    def __init__(self, market_state: dict):
        super().__init__(market_state)
        self.lookback_period = 20
        self.market_data = MarketData(market_state)
        self.volatility_analyzer = VolatilityAnalyzer(market_state)

    def generate_signal(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'binance') -> str:
        """Generate a trading signal based on breakout strategy with dynamic thresholds."""
        try:
            if len(klines) < self.lookback_period:
                logger.warning(f"Not enough data for {symbol} to calculate breakout levels")
                return "hold"

            # Получаем данные с биржи
            klines = self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            
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
    from trading_bot.symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    strategy = BreakoutStrategy(market_state)
    symbol_filter = SymbolFilter(market_state)
    
    # Получаем символы
    symbols = symbol_filter.filter_symbols(strategy.market_data.get_symbols('mexc'), 'mexc')
    
    if symbols:
        signal = strategy.generate_signal(symbols[0], '1h', 30, 'mexc')
        print(f"Signal for {symbols[0]}: {signal}")
    else:
        print("No symbols available for testing")
