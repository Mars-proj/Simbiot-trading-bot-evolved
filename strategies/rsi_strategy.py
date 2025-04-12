from trading_bot.logging_setup import setup_logging
from trading_bot.data_sources.market_data import MarketData
from trading_bot.strategies.strategy import Strategy
from trading_bot.analysis.volatility_analyzer import VolatilityAnalyzer

logger = setup_logging('rsi_strategy')

class RSIStrategy(Strategy):
    def __init__(self, market_state: dict):
        super().__init__(market_state)
        self.rsi_period = 14
        self.market_data = MarketData(market_state)
        self.volatility_analyzer = VolatilityAnalyzer(market_state)

    def calculate_rsi(self, closes: list) -> float:
        """Calculate RSI for the given price data."""
        if len(closes) < self.rsi_period:
            return 50.0  # Нейтральное значение, если данных недостаточно

        gains = []
        losses = []
        for i in range(1, len(closes)):
            diff = closes[i] - closes[i-1]
            if diff > 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(diff))

        avg_gain = sum(gains[-self.rsi_period:]) / self.rsi_period
        avg_loss = sum(losses[-self.rsi_period:]) / self.rsi_period

        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def generate_signal(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'binance') -> str:
        """Generate a trading signal based on RSI strategy with dynamic thresholds."""
        try:
            # Получаем данные с биржи
            klines = self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if len(klines) < self.rsi_period + 1:
                logger.warning(f"Not enough data for {symbol} to calculate RSI")
                return "hold"

            closes = [kline['close'] for kline in klines]
            rsi = self.calculate_rsi(closes)

            # Динамически рассчитываем пороги RSI на основе волатильности
            symbol_volatility = self.volatility_analyzer.analyze_volatility(symbol, exchange_name)
            overbought_threshold = 70 + (symbol_volatility * 10)  # Базовый порог 70, корректируется на волатильность
            oversold_threshold = 30 - (symbol_volatility * 10)    # Базовый порог 30, корректируется на волатильность

            if rsi > overbought_threshold:
                signal = "sell"
            elif rsi < oversold_threshold:
                signal = "buy"
            else:
                signal = "hold"

            logger.info(f"Generated signal for {symbol}: {signal} (RSI: {rsi}, Overbought: {overbought_threshold}, Oversold: {oversold_threshold})")
            return signal
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    from trading_bot.symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    strategy = RSIStrategy(market_state)
    symbol_filter = SymbolFilter(market_state)
    
    # Получаем символы
    symbols = symbol_filter.filter_symbols(strategy.market_data.get_symbols('mexc'), 'mexc')
    
    if symbols:
        signal = strategy.generate_signal(symbols[0], '1h', 30, 'mexc')
        print(f"Signal for {symbols[0]}: {signal}")
    else:
        print("No symbols available for testing")
