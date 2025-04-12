from trading_bot.logging_setup import setup_logging
from trading_bot.strategies.strategy_manager import StrategyManager
from trading_bot.trading.trade_executor import TradeExecutor
from trading_bot.learning.backtest_manager import BacktestManager
from trading_bot.monitoring.monitoring import Monitoring
from trading_bot.data_sources.market_data import MarketData

logger = setup_logging('core')

class TradingBotCore:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.strategy_manager = StrategyManager(market_state)
        self.trade_executor = TradeExecutor(market_state)
        self.backtest_manager = BacktestManager(market_state)
        self.monitoring = Monitoring(market_state)
        self.market_data = MarketData(market_state)

    def run_trading(self, symbol: str, strategy_name: str, account_balance: float, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'binance') -> dict:
        """Run the trading process for a given strategy."""
        try:
            # Получаем данные для символа
            klines = self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            
            # Генерируем сигналы
            signals = self.strategy_manager.generate_signals(klines)[strategy_name]
            
            # Выполняем сделки
            trades = []
            for signal in signals:
                if signal['signal'] in ['buy', 'sell']:
                    trade = self.trade_executor.execute_trade(
                        symbol=symbol,
                        side=signal['signal'],
                        klines=klines,
                        entry_price=klines[-1]['close'],  # Последняя цена
                        stop_loss=klines[-1]['close'] * 0.95,  # Стоп-лосс на 5% ниже
                        account_balance=account_balance
                    )
                    trades.append(trade)
            
            logger.info(f"Trading completed: {trades}")
            return trades
        except Exception as e:
            logger.error(f"Trading failed: {str(e)}")
            raise

    def run_backtest(self, symbols: list, strategies: list, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'binance') -> dict:
        """Run backtesting for multiple symbols and strategies."""
        try:
            results = self.backtest_manager.manage_backtests(symbols, strategies, timeframe, limit, exchange_name)
            logger.info(f"Backtesting completed: {results}")
            return results
        except Exception as e:
            logger.error(f"Backtesting failed: {str(e)}")
            raise

    def run_monitoring(self) -> dict:
        """Run system monitoring."""
        try:
            monitoring_result = self.monitoring.run_monitoring()
            logger.info(f"Monitoring completed: {monitoring_result}")
            return monitoring_result
        except Exception as e:
            logger.error(f"Monitoring failed: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    from trading_bot.symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    core = TradingBotCore(market_state)
    symbol_filter = SymbolFilter(market_state)
    
    # Получаем символы
    symbols = symbol_filter.filter_symbols(core.market_data.get_symbols('binance'), 'binance')
    
    # Run trading
    trades = core.run_trading(symbols[0], 'bollinger', 10000, '1h', 30, 'binance')
    print(f"Trades for {symbols[0]}: {trades}")
    
    # Run backtest
    strategies = ['bollinger', 'rsi']
    backtest_results = core.run_backtest(symbols[:2], strategies, '1h', 30, 'binance')
    print(f"Backtest results: {backtest_results}")
    
    # Run monitoring
    monitoring_result = core.run_monitoring()
    print(f"Monitoring result: {monitoring_result}")
