import requests
import time
from trading_bot.logging_setup import setup_logging
from trading_bot.utils.config_loader import load_config

logger = setup_logging('api_utils')

class APIUtils:
    @staticmethod
    def handle_api_response(response):
        """Handle API response and check for errors."""
        try:
            if response.status_code != 200:
                raise ValueError(f"API request failed: {response.status_code} - {response.text}")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to handle API response: {str(e)}")
            raise

    @staticmethod
    def retry_request(request_func, market_state: dict, max_retries=3, delay=1):
        """Retry a request with exponential backoff, adjusted by market state."""
        try:
            config = load_config(market_state)
            volatility = market_state['volatility']
            # Увеличиваем задержку при высокой волатильности
            adjusted_delay = delay * (1 + volatility)
            for attempt in range(max_retries):
                try:
                    response = request_func()
                    return APIUtils.handle_api_response(response)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed after {max_retries} retries: {str(e)}")
                        raise
                    logger.warning(f"Request failed, retrying ({attempt+1}/{max_retries}): {str(e)}")
                    time.sleep(adjusted_delay * (2 ** attempt))  # Exponential backoff
        except Exception as e:
            logger.error(f"Failed to retry request: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    def test_request():
        return requests.get("https://api.example.com/test")
    market_state = {'volatility': 0.3}
    result = APIUtils.retry_request(test_request, market_state)
    print(f"Result: {result}")
