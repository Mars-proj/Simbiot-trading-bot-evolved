from trading_bot.strategies.strategy import Strategy
from trading_bot.logging_setup import setup_logging
from trading_bot.data_sources.market_data import MarketData

logger = setup_logging('rsi_strategy')

class RSIStrategy(Strategy):
    def __init__(self, market_state: dict):
        super().__init__(market_state)
        self.period = 14
        self.overbought = 70
        self.oversold = 30
        self.market_data = MarketData(market_state)

    def generate_signal(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'binance') -> str:
        """Generate a trading signal based on RSI."""
        try:
            # Получаем данные с биржи
            klines = self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if len(klines) < self.period:
                logger.warning(f"Not enough data for {symbol} to calculate RSI")
                return "hold"

            closes = [kline['close'] for kline in klines[-self.period:]]
            deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
            
            gains = [delta if delta > 0 else 0 for delta in deltas]
            losses = [-delta if delta < 0 else 0 for delta in deltas]
            
            avg_gain = sum(gains) / len(gains)
            avg_loss = sum(losses) / len(losses)
            
            rs = avg_gain / avg_loss if avg_loss != 0 else 0
            rsi = 100 - (100 / (1 + rs)) if rs != 0 else 100

            if rsi > self.overbought:
                signal = "sell"
            elif rsi < self.oversold:
                signal = "buy"
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
    strategy = RSIStrategy(market_state)
    symbol_filter = SymbolFilter(market_state)
    
    # Получаем символы
    symbols = symbol_filter.filter_symbols(strategy.market_data.get_symbols('binance'), 'binance')
    
    if symbols:
        signal = strategy.generate_signal(symbols[0], '1h', 30, 'binance')
        print(f"Signal for {symbols[0]}: {signal}")
    else:
        print("No symbols available for testing")
