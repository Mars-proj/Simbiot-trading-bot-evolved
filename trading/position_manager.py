from trading_bot.logging_setup import setup_logging
from trading_bot.utils.cache_manager import CacheManager

logger = setup_logging('position_manager')

class PositionManager:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.cache = CacheManager(market_state)
        self.positions = {}

    def open_position(self, symbol: str, side: str, quantity: float, entry_price: float) -> dict:
        """Open a new position."""
        try:
            # Динамическая корректировка количества на основе волатильности
            adjusted_quantity = quantity * (1 - self.volatility / 2)
            
            position = {
                'symbol': symbol,
                'side': side,
                'quantity': adjusted_quantity,
                'entry_price': entry_price,
                'status': 'open'
            }
            
            self.positions[symbol] = position
            self.cache.set(f"position_{symbol}", position)
            logger.info(f"Opened position: {position}")
            return position
        except Exception as e:
            logger.error(f"Failed to open position: {str(e)}")
            raise

    def close_position(self, symbol: str, exit_price: float) -> dict:
        """Close an existing position."""
        try:
            position = self.positions.get(symbol)
            if not position:
                logger.warning(f"No position found for {symbol}")
                return {'status': 'failed', 'reason': 'no position'}

            profit = (exit_price - position['entry_price']) * position['quantity'] if position['side'] == 'buy' else (position['entry_price'] - exit_price) * position['quantity']
            
            position['exit_price'] = exit_price
            position['profit'] = profit
            position['status'] = 'closed'
            
            self.cache.set(f"position_{symbol}", position)
            del self.positions[symbol]
            logger.info(f"Closed position: {position}")
            return position
        except Exception as e:
            logger.error(f"Failed to close position: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    manager = PositionManager(market_state)
    position = manager.open_position("BTC/USDT", "buy", 0.1, 50000)
    print(f"Opened position: {position}")
    closed_position = manager.close_position("BTC/USDT", 51000)
    print(f"Closed position: {closed_position}")
