from trading_bot.logging_setup import setup_logging
from trading_bot.strategies.strategy import Strategy
from trading_bot.data_sources.market_data import MarketData

logger = setup_logging('signal_generator')

class SignalGenerator:
    def __init__(self, market_state: dict, strategy: Strategy):
        self.volatility = market_state['volatility']
        self.strategy = strategy
        self.market_data = MarketData(market_state)

    def generate_signals(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'binance') -> list:
        """Generate trading signals for the given symbol."""
        try:
            # Получаем данные с биржи
            klines = self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No klines data for {symbol} on {exchange_name}")
                return []

            signals = []
            for i, kline in enumerate(klines):
                signal = self.strategy.generate_signal(symbol, timeframe, i + 1, exchange_name)
                signals.append({
                    'timestamp': kline['timestamp'],
                    'signal': signal
                })
            
            logger.info(f"Generated {len(signals)} signals for {symbol}")
            return signals
        except Exception as e:
            logger.error(f"Error generating signals for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    from trading_bot.strategies.bollinger_strategy import BollingerStrategy
    from trading_bot.symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    strategy = BollingerStrategy(market_state)
    generator = SignalGenerator(market_state, strategy)
    symbol_filter = SymbolFilter(market_state)
    
    # Получаем символы
    symbols = symbol_filter.filter_symbols(generator.market_data.get_symbols('binance'), 'binance')
    
    if symbols:
        signals = generator.generate_signals(symbols[0], '1h', 30, 'binance')
        print(f"Signals for {symbols[0]}: {signals}")
    else:
        print("No symbols available for testing")
