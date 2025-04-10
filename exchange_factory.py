import ccxt
from dotenv import load_dotenv
import os
from logging_setup import setup_logging

logger = setup_logging('exchange_factory')

class ExchangeFactory:
    @staticmethod
    def create_exchange(exchange_id: str) -> ccxt.Exchange:
        """Create an exchange instance with API keys from .env."""
        try:
            load_dotenv()
            api_key = os.getenv(f'{exchange_id.upper()}_API_KEY')
            api_secret = os.getenv(f'{exchange_id.upper()}_API_SECRET')

            if not api_key or not api_secret:
                logger.error(f"API key or secret not found for {exchange_id} in .env")
                raise ValueError(f"API key or secret not found for {exchange_id}")

            exchange_class = getattr(ccxt, exchange_id)
            exchange = exchange_class({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
            })
            logger.info(f"Created exchange instance for {exchange_id}")
            return exchange
        except Exception as e:
            logger.error(f"Failed to create exchange {exchange_id}: {str(e)}")
            raise
