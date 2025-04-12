from trading_bot.strategies.strategy import Strategy
from trading_bot.logging_setup import setup_logging
from trading_bot.data_sources.market_data import MarketData

logger = setup_logging('bollinger_strategy')

class BollingerStrategy(Strategy):
    def __init__(self, market_state: dict):
        super().__init__(market_state)
        self.period = 20
        self.std_dev = 2.0
        self.market_data = MarketData(market_state)

    def generate_signal(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'binance') -> str:
        """Generate a trading signal based on Bollinger Bands."""
        try:
            # Получаем данные с биржи
            klines = self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if len(klines) < self.period:
                logger.warning(f"Not enough data for {symbol} to calculate Bollinger Bands")
                return "hold"

            closes = [kline['close'] for kline in klines[-self.period:]]
            sma = sum(closes) / len(closes)
            std = (sum((x - sma) ** 2 for x in closes) / len(closes)) ** 0.5
            upper_band = sma + self.std_dev * std
            lower_band = sma - self.std_dev * std

            # Текущая цена — последняя цена закрытия
            price = klines[-1]['close']

            if price > upper_band:
                signal = "sell"
            elif price < lower_band:
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
    strategy = BollingerStrategy(market_state)
    symbol_filter = SymbolFilter(market_state)
    
    # Получаем символы
    symbols = symbol_filter.filter_symbols(strategy.market_data.get_symbols('binance'), 'binance')
    
    if symbols:
        signal = strategy.generate_signal(symbols[0], '1h', 30, 'binance')
        print(f"Signal for {symbols[0]}: {signal}")
    else:
        print("No symbols available for testing")
