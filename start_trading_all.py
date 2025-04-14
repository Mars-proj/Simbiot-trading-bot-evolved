import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core import TradingBotCore
from utils.logging_setup import setup_logging
from data_sources.market_data import SyncMarketData
from learning.online_learning import SyncOnlineLearning

logger = setup_logging('start_trading_all')

def fetch_klines(exchange_name, symbol, timeframe, limit):
    """Fetch klines synchronously."""
    market_data_instance = SyncMarketData()
    try:
        market_data_instance.initialize_exchange(exchange_name)
        klines = market_data_instance.get_klines(symbol, timeframe, limit, exchange_name)
        logger.info(f"Fetched klines for {symbol} on {exchange_name}, result: {type(klines)}")
        return klines
    except Exception as e:
        logger.error(f"Failed to fetch klines for {symbol} on {exchange_name}: {str(e)}")
        return None
    finally:
        market_data_instance.close()

def train_model(symbol, timeframe, limit, exchange_name):
    """Train a model synchronously."""
    market_data_instance = SyncMarketData()
    market_state = {}
    try:
        market_data_instance.initialize_exchange(exchange_name)
        online_learning = SyncOnlineLearning(market_state, market_data_instance)
        result = online_learning.retrain(symbol, timeframe, limit, exchange_name)
        logger.info(f"Model retrained for {symbol} on {exchange_name}, result: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to retrain model for {symbol} on {exchange_name}: {str(e)}")
        return False
    finally:
        market_data_instance.close()

def main():
    bot = TradingBotCore()
    bot.start_trading(fetch_klines, train_model)

if __name__ == "__main__":
    main()
