from trading_bot.logging_setup import setup_logging

logger = setup_logging('error_handler')

class ErrorHandler:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']

    def handle_error(self, error: Exception) -> dict:
        """Handle an error and return a structured response."""
        try:
            error_response = {
                'error_type': type(error).__name__,
                'message': str(error),
                'volatility': self.volatility
            }
            logger.error(f"Error occurred: {error_response}")
            return error_response
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
        response = error_handler.handle_error(e)
        print(f"Error response: {response}")
