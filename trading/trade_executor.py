from trading_bot.logging_setup import setup_logging
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

    def execute_trade(self, symbol: str, side: str, klines: list, entry_price: float, stop_loss: float, account_balance: float) -> dict:
        """Execute a trade based on the given signal."""
        try:
            # Рассчитываем размер позиции
            quantity = self.risk_calculator.calculate_position_size(klines, entry_price, stop_loss, account_balance)
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
    market_state = {'volatility': 0.3}
    executor = TradeExecutor(market_state)
    klines = [{'close': float(50000 + i * 100)} for i in range(10)]
    trade = executor.execute_trade("BTC/USDT", "buy", klines, 50000, 49000, 10000)
    print(f"Trade: {trade}")
