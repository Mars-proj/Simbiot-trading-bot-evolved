import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import asyncio
from utils.logging_setup import setup_logging
from strategies.strategy_manager import StrategyManager
from trading.trade_executor import TradeExecutor
from learning.backtest_manager import BacktestManager
from monitoring.monitoring import Monitoring
from data_sources.market_data import MarketData
from analysis.volatility_analyzer import VolatilityAnalyzer
from learning.online_learning import OnlineLearning

logger = setup_logging('core')

class TradingBotCore:
    def __init__(self, market_state: dict, market_data: MarketData):
        self.volatility = market_state['volatility']
        self.strategy_manager = StrategyManager(market_state, market_data=market_data)
        self.trade_executor = TradeExecutor(market_state, market_data=market_data)
        self.backtest_manager = BacktestManager(market_state, market_data=market_data)
        self.monitoring = Monitoring(market_state)
        self.market_data = market_data
        self.volatility_analyzer = VolatilityAnalyzer(market_state, market_data=market_data)
        self.online_learning = OnlineLearning(market_state, market_data=market_data)

    async def run_trading(self, symbol: str, strategy_name: str, account_balance: float, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'mexc') -> dict:
        """Run the trading process for a given strategy and retrain ML model."""
        try:
            # Получаем данные для символа
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            
            # Генерируем сигналы
            signals_dict = await self.strategy_manager.generate_signals(symbol, timeframe, limit, exchange_name)
            signal = signals_dict[strategy_name]
            
            # Динамически рассчитываем стоп-лосс на основе волатильности
            symbol_volatility = await self.volatility_analyzer.analyze_volatility(symbol, exchange_name)
            stop_loss_percentage = 0.05 * (1 + symbol_volatility)  # Базовый стоп-лосс 5%, корректируется на волатильность
            
            # Выполняем сделки
            trades = []
            if signal in ['buy', 'sell']:
                trade = self.trade_executor.execute_trade(
                    symbol=symbol,
                    side=signal,
                    klines=klines,
                    entry_price=klines[-1]['close'],  # Последняя цена
                    stop_loss=klines[-1]['close'] * (1 - stop_loss_percentage),  # Динамический стоп-лосс
                    account_balance=account_balance
                )
                trades.append(trade)
            
            # Переобучаем ML-модель после каждой торговой итерации
            await self.online_learning.retrain_model([symbol], timeframe, 100, exchange_name)
            
            logger.info(f"Trading completed: {trades}")
            return trades
        except Exception as e:
            logger.error(f"Trading failed: {str(e)}")
            raise

    async def run_backtest(self, symbols: list, strategies: list, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'mexc') -> dict:
        """Run backtesting for multiple symbols and strategies."""
        try:
            results = await self.backtest_manager.manage_backtests(symbols, strategies, timeframe, limit, exchange_name)
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
    import asyncio
    from symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    market_data = MarketData(market_state)
    core = TradingBotCore(market_state, market_data=market_data)
    symbol_filter = SymbolFilter(market_state, market_data=market_data)
    
    async def main():
        # Получаем символы
        symbols = await core.market_data.get_symbols('mexc')
        symbols = await symbol_filter.filter_symbols(symbols, 'mexc')
        
        # Run trading
        trades = await core.run_trading(symbols[0], 'bollinger', 10000, '1h', 30, 'mexc')
        print(f"Trades for {symbols[0]}: {trades}")
        
        # Run backtest
        strategies = ['bollinger', 'rsi']
        backtest_results = await core.run_backtest(symbols[:2], strategies, '1h', 30, 'mexc')
        print(f"Backtest results: {backtest_results}")
        
        # Run monitoring
        monitoring_result = core.run_monitoring()
        print(f"Monitoring result: {monitoring_result}")

    asyncio.run(main())
