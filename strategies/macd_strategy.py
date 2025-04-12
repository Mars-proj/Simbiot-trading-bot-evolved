from trading_bot.strategies.strategy import Strategy
from trading_bot.logging_setup import setup_logging
from trading_bot.data_sources.market_data import MarketData

logger = setup_logging('macd_strategy')

class MACDStrategy(Strategy):
    def __init__(self, market_state: dict):
        super().__init__(market_state)
        self.short_period = 12
        self.long_period = 26
        self.signal_period = 9
        self.market_data = MarketData(market_state)

    def generate_signal(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'binance') -> str:
        """Generate a trading signal based on MACD."""
        try:
            # Получаем данные с биржи
            klines = self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if len(klines) < self.long_period:
                logger.warning(f"Not enough data for {symbol} to calculate MACD")
                return "hold"

            closes = [kline['close'] for kline in klines]
            
            # Calculate EMAs
            def ema(period, data):
                alpha = 2 / (period + 1)
                ema_values = [data[0]]
                for i in range(1, len(data)):
                    ema_values.append(alpha * data[i] + (1 - alpha) * ema_values[-1])
                return ema_values
            
            short_ema = ema(self.short_period, closes[-self.long_period:])
            long_ema = ema(self.long_period, closes[-self.long_period:])
            macd = [short - long for short, long in zip(short_ema, long_ema)]
            
            # Calculate signal line
            signal_line = ema(self.signal_period, macd[-self.signal_period:])
            
            # Latest MACD and signal values
            macd_latest = macd[-1]
            signal_latest = signal_line[-1]

            if macd_latest > signal_latest:
                signal = "buy"
            elif macd_latest < signal_latest:
                signal = "sell"
            else:
                signal = "hold"

            logger.info(f"Generated signal for {symbol}: {signal}")
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
    symbols = symbol_filter.filter_symbols(strategy.market_data.get_symbols('binance'), 'binance')
    
    if symbols:
        signal = strategy.generate_signal(symbols[0], '1h', 30, 'binance')
        print(f"Signal for {symbols[0]}: {signal}")
    else:
        print("No symbols available for testing"
