import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from .logging_setup import setup_logging

logger = setup_logging('data_utils')

class DataUtils:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']

    def normalize_data(self, data: list) -> list:
        """Normalize a list of numerical data."""
        try:
            if not data:
                logger.warning("Empty data list provided for normalization")
                return []

            min_val = min(data)
            max_val = max(data)
            if max_val == min_val:
                logger.warning("Data has no range for normalization")
                return [0] * len(data)

            normalized = [(x - min_val) / (max_val - min_val) for x in data]
            logger.debug(f"Normalized data: {normalized}")
            return normalized
        except Exception as e:
            logger.error(f"Failed to normalize data: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    data_utils = DataUtils(market_state)
    data = [1, 2, 3, 4, 5]
    normalized = data_utils.normalize_data(data)
    print(f"Normalized data: {normalized}")
