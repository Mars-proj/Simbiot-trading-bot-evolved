from celery import Celery
from celery.schedules import crontab
from logging_setup import setup_logging
import pandas as pd

app = Celery('trading_bot', broker='redis://localhost:6379/0')
logger = setup_logging('celery_app')

# From queue_manager.py
def add_to_queue(task: str, *args):
    """Add a task to the queue."""
    try:
        logger.info(f"Adding task {task} to queue with args {args}")
        result = app.send_task(task, args=args)
        logger.info(f"Task {task} added to queue: {result.id}")
        return result
    except Exception as e:
        logger.error(f"Failed to add task {task} to queue: {str(e)}")
        raise

@app.task
def run_backtest_task(strategy_id: int, data: dict):
    """Run a backtest task."""
    try:
        logger.info(f"Running backtest for strategy {strategy_id}")
        from backtest_manager import BacktestManager
        from strategies import get_strategy_by_id
        strategy = get_strategy_by_id(strategy_id)
        manager = BacktestManager()
        result = manager.run_multiple_backtests([strategy], data)
        logger.info(f"Backtest completed for strategy {strategy_id}: {result}")
        return result
    except Exception as e:
        logger.error(f"Backtest failed for strategy {strategy_id}: {str(e)}")
        raise

@app.task
def retrain_model_task(model_id: int):
    """Retrain an ML model."""
    try:
        logger.info(f"Retraining model {model_id}")
        from ml_model_trainer import train_model
        from data_utils import load_historical_data
        data = load_historical_data('binance', 'BTC/USDT', '1h', limit=1000)
        train_model(model_id, data)
        logger.info(f"Model {model_id} retrained successfully")
    except Exception as e:
        logger.error(f"Failed to retrain model {model_id}: {str(e)}")
        raise

@app.task
def generate_strategy_task(data: dict):
    """Generate and optimize a new strategy."""
    try:
        logger.info("Generating new strategy")
        from strategy_manager import StrategyManager
        manager = StrategyManager('binance')
        manager.generate_new_strategy(pd.DataFrame(data))
        logger.info("New strategy generated and optimized")
    except Exception as e:
        logger.error(f"Failed to generate strategy: {str(e)}")
        raise

@app.task
def trade_execution_task(symbol: str, signal: str, amount: float):
    """Execute a trade."""
    try:
        logger.info(f"Executing trade: {signal} for {symbol}, amount {amount}")
        from exchange_factory import ExchangeFactory
        exchange = ExchangeFactory.create_exchange('binance')
        exchange.execute_trade({"symbol": symbol, "side": signal, "amount": amount})
        logger.info(f"Trade executed: {signal} for {symbol}")
    except Exception as e:
        logger.error(f"Failed to execute trade for {symbol}: {str(e)}")
        raise

app.conf.beat_schedule = {
    'retrain-model-every-hour': {
        'task': 'celery_app.retrain_model_task',
        'schedule': crontab(minute=0, hour='*'),
        'args': (1,)
    },
    'generate-strategy-every-day': {
        'task': 'celery_app.generate_strategy_task',
        'schedule': crontab(minute=0, hour=0),
        'args': (pd.DataFrame({'price': [10000 + i for i in range(1000)]}).to_dict(),)
    }
}
