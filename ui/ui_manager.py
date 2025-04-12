from trading_bot.logging_setup import setup_logging
from trading_bot.utils.performance_tracker import PerformanceTracker
from trading_bot.trading.trade_executor import TradeExecutor
from trading_bot.symbol_filter import SymbolFilter
from trading_bot.data_sources.market_data import MarketData
from .dashboard import Dashboard
from .performance_charts import PerformanceCharts
from .trade_visualizer import TradeVisualizer

logger = setup_logging('ui_manager')

class UIManager:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.performance_tracker = PerformanceTracker(market_state)
        self.trade_executor = TradeExecutor(market_state)
        self.symbol_filter = SymbolFilter(market_state)
        self.market_data = MarketData(market_state)
        self.dashboard = Dashboard(market_state)
        self.performance_charts = PerformanceCharts(market_state)
        self.trade_visualizer = TradeVisualizer(market_state)

    def run_ui(self, symbol: str, strategy: str, account_balance: float, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'binance') -> None:
        """Run the UI components."""
        try:
            # Получаем метрики производительности
            metrics = self.performance_tracker.get_metrics()
            
            # Получаем реальные сделки
            trades = self.trade_executor.execute_trade(symbol, 'buy', account_balance, timeframe, limit, exchange_name)
            if not isinstance(trades, list):
                trades = [trades]  # Если возвращена одна сделка, преобразуем в список

            # Запускаем UI-компоненты
            self.dashboard.display_metrics(metrics)
            self.performance_charts.plot_metrics()
            self.trade_visualizer.visualize_trades(symbol, strategy, account_balance, timeframe, limit, exchange_name)
            
            logger.info(f"UI components executed successfully for {symbol}")
        except Exception as e:
            logger.error(f"Failed to run UI for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    ui_manager = UIManager(market_state)
    
    # Получаем символы
    symbols = ui_manager.symbol_filter.filter_symbols(ui_manager.market_data.get_symbols('binance'), 'binance')
    
    if symbols:
        ui_manager.run_ui(symbols[0], 'bollinger', 10000, '1h', 30, 'binance')
    else:
        print("No symbols available for UI")
