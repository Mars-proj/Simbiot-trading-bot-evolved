from trading_bot.logging_setup import setup_logging

logger = setup_logging('order_utils')

class OrderUtils:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']

    def calculate_commission(self, quantity: float, price: float, commission_rate: float = 0.001) -> float:
        """Calculate commission for an order."""
        try:
            # Динамическая корректировка комиссии на основе волатильности
            adjusted_rate = commission_rate * (1 + self.volatility / 2)
            commission = quantity * price * adjusted_rate
            logger.info(f"Calculated commission: {commission} (rate: {adjusted_rate})")
            return commission
        except Exception as e:
            logger.error(f"Failed to calculate commission: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    utils = OrderUtils(market_state)
    commission = utils.calculate_commission(0.1, 50000)
    print(f"Commission: {commission}")
