import json
import os
from trading_bot.logging_setup import setup_logging

logger = setup_logging('config_loader')

class ConfigLoader:
    def __init__(self, market_state: dict, config_path: str = "config.json"):
        self.volatility = market_state['volatility']
        self.config_path = config_path

    def load_config(self) -> dict:
        """Load configuration from a JSON file."""
        try:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"Config file not found: {self.config_path}")
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded config from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config from {self.config_path}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    config_loader = ConfigLoader(market_state)
    config = config_loader.load_config()
    print(f"Loaded config: {config}")
