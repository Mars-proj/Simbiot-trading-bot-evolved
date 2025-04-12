from trading_bot.logging_setup import setup_logging
from trading_bot.data_sources.market_data import MarketData
from trading_bot.strategies.strategy import Strategy
from trading_bot.analysis.volatility_analyzer import VolatilityAnalyzer

logger = setup_logging('scalping_strategy')

class ScalpingStrategy(Strategy):
    def __init__(self, market_state: dict):
        super().__init__(market_state)
        self.lookback_period = 5
        self.market_data = MarketData(market_state)
        self.volatility_analyzer = VolatilityAnalyzer(market_state)

    def generate_signal(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'binance') -> str:
        """Generate a trading signal based on scalping strategy with dynamic thresholds."""
        try:
            # Получаем данные с биржи
            klines = self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if len(klines) < self.lookback_period:
                logger.warning(f"Not enough data for {symbol} to calculate scalping levels")
                return "hold"

            closes = [kline['close'] for kline in klines[-self.lookback_period:]]
            avg_price = sum(closes) / len(closes)

            # Динамически рассчитываем порог на основе волатильности
            symbol_volatility = self.volatility_analyzer.analyze_volatility(symbol, exchange_name)
            threshold = 0.005 * (1 + symbol_volatility)  # Базовый порог 0.5%, корректируется на волатильность

            price = klines[-1]['close']
            price_change = (price - avg_price) / avg_price

            if price_change > threshold:
                signal = "sell"
            elif price_change < -threshold:
                signal = "buy"
            else:
                signal = "hold"

            logger.info(f"Generated signal for {symbol}: {signal} (Price: {price}, Avg Price: {avg_price}, Threshold: {threshold})")
            return signal
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    from trading_bot.symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    strategy = ScalpingStrategy(market_state)
    symbol_filter = SymbolFilter(market_state)
    
    # Получаем символы
    symbols = symbol_filter.filter_symbols(strategy.market_data.get_symbols('mexc'), 'mexc')
    
    if symbols:
        signal = strategy.generate_signal(symbols[0], '1h', 30, 'mexc')
        print(f"Signal for {symbols[0]}: {signal}")
    else:
        print("No symbols available for testing")
