from trading_bot.logging_setup import setup_logging
from trading_bot.celery_app import retrain_model_task

logger = setup_logging('retraining_manager')

def schedule_retraining(model_id: int) -> None:
    """Schedule model retraining."""
    try:
        logger.info(f"Scheduling retraining for model {model_id}")
        retrain_model_task.delay(model_id)
        logger.info(f"Retraining task for model {model_id} scheduled")
    except Exception as e:
        logger.error(f"Failed to schedule retraining for model {model_id}: {str(e)}")
        raise
