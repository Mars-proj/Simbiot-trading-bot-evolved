import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from .logging_setup import setup_logging

logger = setup_logging('api_utils')

class APIUtils:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']

    def handle_response(self, response: dict) -> dict:
        """Handle API response and check for errors."""
        try:
            if 'error' in response and response['error']:
                logger.error(f"API error: {response['error']}")
                raise Exception(response['error'])
            logger.debug(f"API response: {response}")
            return response
        except Exception as e:
            logger.error(f"Failed to handle API response: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    api_utils = APIUtils(market_state)
    
    response = {'data': 'test', 'error': None}
    result = api_utils.handle_response(response)
    print(f"Handled response: {result}")
