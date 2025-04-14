import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
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
    """Celery task to fetch klines for a symbol."""
    from data_sources.market_data import MarketData
    market_data = MarketData()
    try:
        # Run async operation synchronously
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(market_data.initialize_exchange(exchange_name))
        klines = loop.run_until_complete(market_data.get_klines(symbol, timeframe, limit, exchange_name))
        loop.run_until_complete(market_data.close())
        logger.info(f"Fetched klines for {symbol} on {exchange_name}")
        return klines
    except Exception as e:
        logger.error(f"Failed to fetch klines for {symbol} on {exchange_name}: {str(e)}")
        return None
    finally:
        if not loop.is_running():
            loop.close()

@app.task
def train_model_task(symbol, timeframe, limit, exchange_name):
    """Celery task to train a model for a symbol."""
    from learning.online_learning import OnlineLearning
    from data_sources.market_data import MarketData
    market_data = MarketData()
    market_state = {}
    try:
        # Run async operation synchronously
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(market_data.initialize_exchange(exchange_name))
        online_learning = OnlineLearning(market_state, market_data)
        loop.run_until_complete(online_learning.retrain(symbol, timeframe, limit, exchange_name))
        loop.run_until_complete(market_data.close())
        logger.info(f"Model retrained for {symbol} on {exchange_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to retrain model for {symbol} on {exchange_name}: {str(e)}")
        return False
    finally:
        if not loop.is_running():
            loop.close()
