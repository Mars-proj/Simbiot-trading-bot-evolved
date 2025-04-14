import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_setup import setup_logging

logger = setup_logging('position_manager')

class PositionManager:
    def __init__(self, max_position_size=0.1):
        """Initialize the Position Manager."""
        self.max_position_size = max_position_size  # Maximum position size (10% of capital)
        self.positions = {}  # Dictionary to store positions: {symbol: size}
        self.capital = 10000  # Default capital, can be updated

    def set_capital(self, capital):
        """Set the trading capital."""
        self.capital = capital
        logger.info(f"Trading capital set to {self.capital}")

    def add_position(self, symbol, size):
        """Add a position for a symbol."""
        try:
            max_allowed_size = self.capital * self.max_position_size
            if symbol in self.positions:
                new_size = self.positions[symbol] + size
                if new_size > max_allowed_size:
                    logger.warning(f"Position size {new_size} for {symbol} exceeds limit {max_allowed_size}")
                    return False
                self.positions[symbol] = new_size
            else:
                if size > max_allowed_size:
                    logger.warning(f"Position size {size} for {symbol} exceeds limit {max_allowed_size}")
                    return False
                self.positions[symbol] = size
            logger.info(f"Added position for {symbol}: size {size}")
            return True
        except Exception as e:
            logger.error(f"Failed to add position for {symbol}: {str(e)}")
            return False

    def remove_position(self, symbol, size):
        """Remove a position for a symbol."""
        try:
            if symbol in self.positions:
                self.positions[symbol] -= size
                if self.positions[symbol] <= 0:
                    del self.positions[symbol]
                logger.info(f"Removed position for {symbol}: size {size}")
            else:
                logger.warning(f"No position found for {symbol}")
        except Exception as e:
            logger.error(f"Failed to remove position for {symbol}: {str(e)}")

    def get_position(self, symbol):
        """Get the current position size for a symbol."""
        return self.positions.get(symbol, 0)
