from trading_bot.logging_setup import setup_logging
from trading_bot.core import TradingBotCore

logger = setup_logging('start_trading_all')

class StartTradingAll:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.core = TradingBotCore(market_state)

    def start_all(self, klines: dict, strategies: list, symbols: list, account_balance: float):
        """Start trading for all symbols and strategies."""
        try:
            results = {}
            for symbol in symbols:
                symbol_results = {}
                for strategy in strategies:
                    # Динамическая корректировка баланса на основе волатильности
                    adjusted_balance = account_balance * (1 - self.volatility / 2)
                    
                    trades = self.core.run_trading(klines[symbol], strategy, symbol, adjusted_balance)
                    symbol_results[strategy] = trades
                results[symbol] = symbol_results
            
            logger.info(f"Trading started for all symbols: {results}")
            return results
        except Exception as e:
            logger.error(f"Failed to start trading for all: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    starter = StartTradingAll(market_state)
    klines = {
        'BTC/USDT': [{'timestamp': i, 'close': float(50000 + i * 100)} for i in range(30)],
        'ETH/USDT': [{'timestamp': i, 'close': float(3000 + i * 50)} for i in range(30)]
    }
    strategies = ['bollinger', 'rsi']
    symbols = ['BTC/USDT', 'ETH/USDT']
    results = starter.start_all(klines, strategies, symbols, 10000)
    print(f"Trading results: {results}")
