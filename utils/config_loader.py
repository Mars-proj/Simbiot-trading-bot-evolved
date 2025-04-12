import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from .logging_setup import setup_logging
from dotenv import load_dotenv

logger = setup_logging('config_loader')

class ConfigLoader:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        load_dotenv()

    def load_config(self, key: str) -> str:
        """Load configuration value from .env file."""
        try:
            value = os.getenv(key)
            if value is None:
                logger.error(f"Configuration key {key} not found in .env file")
                raise ValueError(f"Configuration key {key} not found")
            logger.debug(f"Loaded config: {key}={value}")
            return value
        except Exception as e:
            logger.error(f"Failed to load config for key {key}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    config_loader = ConfigLoader(market_state)
    api_key = config_loader.load_config("MEXC_API_KEY")
    print(f"MEXC API Key: {api_key}")
