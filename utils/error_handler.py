import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from .logging_setup import setup_logging

logger = setup_logging('error_handler')

class ErrorHandler:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']

    def handle_error(self, error: Exception) -> None:
        """Handle and log errors."""
        try:
            logger.error(f"Error occurred: {str(error)}")
            raise error
        except Exception as e:
            logger.error(f"Failed to handle error: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    error_handler = ErrorHandler(market_state)
    
    try:
        raise ValueError("Test error")
    except Exception as e:
        error_handler.handle_error(e)
