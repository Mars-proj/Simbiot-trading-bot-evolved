import logging
from celery_app import retrain_model_task

def setup_logging():
    logging.basicConfig(
        filename='retraining.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def schedule_retraining(model_id: int) -> None:
    """Schedule model retraining."""
    setup_logging()
    try:
        logging.info(f"Scheduling retraining for model {model_id}")
        retrain_model_task.delay(model_id)
        logging.info(f"Retraining task for model {model_id} scheduled")
    except Exception as e:
        logging.error(f"Failed to schedule retraining for model {model_id}: {str(e)}")
        raise
