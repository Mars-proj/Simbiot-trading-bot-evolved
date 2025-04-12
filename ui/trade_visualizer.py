import matplotlib.pyplot as plt
from trading_bot.logging_setup import setup_logging
from trading_bot.trading.trade_executor import TradeExecutor
from trading_bot.symbol_filter import SymbolFilter
from trading_bot.data_sources.market_data import MarketData

logger = setup_logging('trade_visualizer')

class TradeVisualizer:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.trade_executor = TradeExecutor(market_state)
        self.symbol_filter = SymbolFilter(market_state)
        self.market_data = MarketData(market_state)

    def visualize_trades(self, symbol: str, strategy: str, account_balance: float, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'binance') -> None:
        """Visualize trades on a plot."""
        try:
            # Выполняем торговлю для получения реальных сделок
            trades = self.trade_executor.execute_trade(symbol, 'buy', account_balance, timeframe, limit, exchange_name)
            if not isinstance(trades, list):
                trades = [trades]  # Если возвращена одна сделка, преобразуем в список

            if not trades:
                logger.warning(f"No trades to visualize for {symbol}")
                return

            timestamps = [trade['timestamp'] if 'timestamp' in trade else i for i, trade in enumerate(trades)]
            prices = [trade['entry_price'] for trade in trades]
            sides = [trade['side'] for trade in trades]

            plt.figure(figsize=(10, 5))
            for i, (ts, price, side) in enumerate(zip(timestamps, prices, sides)):
                color = 'g' if side == 'buy' else 'r'
                plt.plot(ts, price, 'o', color=color, label=side if i == 0 else "")
            plt.xlabel('Timestamp')
            plt.ylabel('Price')
            plt.title(f'Trade Visualization for {symbol}')
            plt.legend()
            plt.grid()
            plt.show()
            logger.info(f"Visualized trades for {symbol}")
        except Exception as e:
            logger.error(f"Failed to visualize trades for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    visualizer = TradeVisualizer(market_state)
    
    # Получаем символы
    symbols = visualizer.symbol_filter.filter_symbols(visualizer.market_data.get_symbols('binance'), 'binance')
    
    if symbols:
        visualizer.visualize_trades(symbols[0], 'bollinger', 10000, '1h', 30, 'binance')
    else:
        print("No symbols available for visualization")
