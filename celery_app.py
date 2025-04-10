from celery import Celery
from celery.schedules import crontab

app = Celery('trading_bot', broker='redis://localhost:6379/0')

# From queue_manager.py
def add_to_queue(task: str, *args):
    """Add a task to the queue."""
    app.send_task(task, args=args)

@app.task
def run_backtest_task(strategy_id: int, data: dict):
    from backtest_manager import BacktestManager
    from strategies import get_strategy_by_id
    strategy = get_strategy_by_id(strategy_id)
    manager = BacktestManager()
    return manager.run_multiple_backtests([strategy], data)

@app.task
def retrain_model_task(model_id: int):
    from ml_model_trainer import train_model
    return train_model(model_id)

app.conf.beat_schedule = {
    'retrain-model-every-hour': {
        'task': 'celery_app.retrain_model_task',
        'schedule': crontab(minute=0, hour='*'),
        'args': (1,)
    }
}
