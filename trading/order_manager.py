from trading_bot.logging_setup import setup_logging
from trading_bot.utils.cache_manager import CacheManager

logger = setup_logging('order_manager')

class OrderManager:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.cache = CacheManager(market_state)
        self.min_order_size = 10.0  # Минимальный размер ордера в USD

    def place_order(self, symbol: str, side: str, quantity: float, price: float) -> dict:
        """Place a new order."""
        try:
            # Проверяем минимальный размер ордера
            order_value = quantity * price
            if order_value < self.min_order_size:
                logger.warning(f"Order value {order_value} USD is below minimum {self.min_order_size} USD")
                return {'status': 'rejected', 'reason': 'below minimum order size'}

            # Динамическая корректировка количества на основе волатильности
            adjusted_quantity = quantity * (1 - self.volatility / 2)
            
            order = {
                'symbol': symbol,
                'side': side,
                'quantity': adjusted_quantity,
                'price': price,
                'status': 'placed'
            }
            
            # Сохраняем ордер в кэше
            self.cache.set(f"order_{symbol}_{side}_{price}", order)
            logger.info(f"Placed order: {order}")
            return order
        except Exception as e:
            logger.error(f"Failed to place order: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    manager = OrderManager(market_state)
    order = manager.place_order("BTC/USDT", "buy", 0.1, 50000)
    print(f"Order: {order}")
