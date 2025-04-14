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
async def fetch_klines_task(exchange_name, symbol, timeframe, limit):
    """Celery task to fetch klines for a symbol."""
    from data_sources.market_data import MarketData
    market_data = MarketData()
    try:
        await market_data.initialize_exchange(exchange_name)
        klines = await market_data.get_klines(symbol, timeframe, limit, exchange_name)
        await market_data.close()
        return klines
    except Exception as e:
        logger.error(f"Failed to fetch klines for {symbol} on {exchange_name}: {str(e)}")
        return None

@app.task
async def train_model_task(symbol, timeframe, limit, exchange_name):
    """Celery task to train a model for a symbol."""
    from learning.online_learning import OnlineLearning
    from data_sources.market_data import MarketData
    market_data = MarketData()
    market_state = {}
    try:
        await market_data.initialize_exchange(exchange_name)
        online_learning = OnlineLearning(market_state, market_data)
        await online_learning.retrain(symbol, timeframe, limit, exchange_name)
        await market_data.close()
        logger.info(f"Model retrained for {symbol} on {exchange_name}")
    except Exception as e:
        logger.error(f"Failed to retrain model for {symbol} on {exchange_name}: {str(e)}")
