import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from celery import Celery
from utils.logging_setup import setup_logging

logger = setup_logging('celery_app')

app = Celery('trading_bot',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0')

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@app.task
def fetch_klines_task(exchange_name, symbol, timeframe, limit):
    """Celery task to fetch klines for a symbol synchronously."""
    from data_sources.market_data import SyncMarketData
    market_data = SyncMarketData()
    try:
        market_data.initialize_exchange(exchange_name)
        klines = market_data.get_klines(symbol, timeframe, limit, exchange_name)
        logger.info(f"Fetched klines for {symbol} on {exchange_name}")
        return klines
    except Exception as e:
        logger.error(f"Failed to fetch klines for {symbol} on {exchange_name}: {str(e)}")
        return None
    finally:
        market_data.close()

@app.task
def train_model_task(symbol, timeframe, limit, exchange_name):
    """Celery task to train a model for a symbol synchronously."""
    from learning.online_learning import SyncOnlineLearning
    from data_sources.market_data import SyncMarketData
    market_data = SyncMarketData()
    market_state = {}
    try:
        market_data.initialize_exchange(exchange_name)
        online_learning = SyncOnlineLearning(market_state, market_data)
        online_learning.retrain(symbol, timeframe, limit, exchange_name)
        logger.info(f"Model retrained for {symbol} on {exchange_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to retrain model for {symbol} on {exchange_name}: {str(e)}")
        return False
    finally:
        market_data.close()
