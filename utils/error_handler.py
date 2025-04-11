from trading_bot.logging_setup import setup_logging
from trading_bot.utils.telegram_notifier import TelegramNotifier

logger = setup_logging('error_handler')

class ErrorHandler:
    def __init__(self, market_state: dict):
        self.notifier = TelegramNotifier(market_state)

    def handle(self, error: Exception, context: str = "General"):
        """Handle errors by logging and sending notifications."""
        try:
            error_message = f"Error in {context}: {str(error)}"
            logger.error(error_message)
            self.notifier.notify(error_message)
        except Exception as e:
            logger.error(f"Failed to handle error: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    handler = ErrorHandler(market_state)
    try:
        raise ValueError("Test error")
    except Exception as e:
        handler.handle(e, context="TestContext")
