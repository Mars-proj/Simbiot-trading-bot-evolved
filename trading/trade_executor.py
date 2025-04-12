from trading_bot.logging_setup import setup_logging
from trading_bot.data_sources.market_data import MarketData
from .order_manager import OrderManager
from .position_manager import PositionManager
from .risk_calculator import RiskCalculator

logger = setup_logging('trade_executor')

class TradeExecutor:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.order_manager = OrderManager(market_state)
        self.position_manager = PositionManager(market_state)
        self.risk_calculator = RiskCalculator(market_state)
        self.market_data = MarketData(market_state)

    def execute_trade(self, symbol: str, side: str, account_balance: float, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'binance') -> dict:
        """Execute a trade based on the given signal."""
        try:
            # Получаем данные для расчёта
            klines = self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No klines data for {symbol} on {exchange_name}")
                return {'status': 'failed', 'reason': 'no data'}

            # Получаем текущую цену и устанавливаем стоп-лосс
            entry_price = klines[-1]['close']
            stop_loss = entry_price * 0.95  # 5% ниже

            # Рассчитываем размер позиции
            quantity = self.risk_calculator.calculate_position_size(symbol, entry_price, stop_loss, account_balance, timeframe, limit, exchange_name)
            if quantity <= 0:
                logger.warning("Invalid position size, trade not executed")
                return {'status': 'failed', 'reason': 'invalid position size'}

            # Размещаем ордер
            order = self.order_manager.place_order(symbol, side, quantity, entry_price)
            if order['status'] != 'placed':
                logger.warning(f"Order placement failed: {order['reason']}")
                return order

            # Открываем позицию
            position = self.position_manager.open_position(symbol, side, quantity, entry_price)
            logger.info(f"Trade executed: {position}")
            return position
        except Exception as e:
            logger.error(f"Failed to execute trade: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    from trading_bot.symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    executor = TradeExecutor(market_state)
    symbol_filter = SymbolFilter(market_state)
    
    # Получаем символы
    symbols = symbol_filter.filter_symbols(executor.market_data.get_symbols('binance'), 'binance')
    
    if symbols:
        account_balance = 10000
        trade = executor.execute_trade(symbols[0], "buy", account_balance, '1h', 30, 'binance')
        print(f"Trade for {symbols[0]}: {trade}")
    else:
        print("No symbols available for testing")
