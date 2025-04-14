from utils.logging_setup import setup_logging

logger = setup_logging('order_manager')

class OrderManager:
    def __init__(self):
        pass

    def place_order(self, symbol, side, quantity):
        logger.info(f"Placing {side} order for {symbol}: {quantity}")
        return {"status": "success"}  # Пример
