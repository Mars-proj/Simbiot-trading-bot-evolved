import time
from datetime import datetime
from trading_bot.logging_setup import setup_logging

logger = setup_logging('time_utils')

class TimeUtils:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']

    def get_current_timestamp(self) -> int:
        """Get the current timestamp in seconds."""
        try:
            timestamp = int(time.time())
            logger.info(f"Retrieved current timestamp: {timestamp}")
            return timestamp
        except Exception as e:
            logger.error(f"Failed to get current timestamp: {str(e)}")
            raise

    def format_timestamp(self, timestamp: int) -> str:
        """Format a timestamp into a human-readable string."""
        try:
            formatted = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"Formatted timestamp {timestamp} to {formatted}")
            return formatted
        except Exception as e:
            logger.error(f"Failed to format timestamp {timestamp}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    time_utils = TimeUtils(market_state)
    timestamp = time_utils.get_current_timestamp()
    formatted = time_utils.format_timestamp(timestamp)
    print(f"Current timestamp: {timestamp}")
    print(f"Formatted timestamp: {formatted}")
