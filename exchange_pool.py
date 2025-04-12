from trading_bot.logging_setup import setup_logging
from trading_bot.exchange_factory import ExchangeFactory

logger = setup_logging('exchange_pool')

class ExchangePool:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.factory = ExchangeFactory(market_state)
        self.exchanges = {}

    def add_exchange(self, exchange_name: str):
        """Add an exchange to the pool."""
        try:
            exchange = self.factory.get_exchange(exchange_name)
            self.exchanges[exchange_name] = exchange
            logger.info(f"Added exchange {exchange_name} to pool")
        except Exception as e:
            logger.error(f"Failed to add exchange {exchange_name}: {str(e)}")
            raise

    def get_exchange(self, exchange_name: str):
        """Get an exchange from the pool."""
        try:
            exchange = self.exchanges.get(exchange_name)
            if not exchange:
                raise ValueError(f"Exchange {exchange_name} not found in pool")
            logger.info(f"Retrieved exchange {exchange_name} from pool")
            return exchange
        except Exception as e:
            logger.error(f"Failed to get exchange {exchange_name}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    pool = ExchangePool(market_state)
    pool.add_exchange('binance')
    exchange = pool.get_exchange('binance')
    print(f"Exchange from pool: {exchange}")
