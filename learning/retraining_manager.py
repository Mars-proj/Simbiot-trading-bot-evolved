from trading_bot.logging_setup import setup_logging
from .online_learning import OnlineLearning

logger = setup_logging('retraining_manager')

class RetrainingManager:
    def __init__(self, market_state: dict, retrain_interval: int = 100):
        self.volatility = market_state['volatility']
        self.retrain_interval = retrain_interval
        self.learner = OnlineLearning(market_state)
        self.trade_count = 0

    def should_retrain(self):
        """Check if retraining is needed."""
        try:
            self.trade_count += 1
            if self.trade_count >= self.retrain_interval:
                # Динамическая корректировка интервала на основе волатильности
                adjusted_interval = self.retrain_interval * (1 - self.volatility / 2)
                if self.trade_count >= adjusted_interval:
                    self.trade_count = 0
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to check retraining condition: {str(e)}")
            raise

    def retrain(self, X_new, y_new):
        """Retrain the model with new data."""
        try:
            if self.should_retrain():
                self.learner.update_model(X_new, y_new)
                logger.info("Model retrained successfully")
            else:
                logger.info("No retraining needed at this time")
        except Exception as e:
            logger.error(f"Failed to retrain model: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    import numpy as np
    market_state = {'volatility': 0.3}
    manager = RetrainingManager(market_state)
    X_new = np.array([[50000 + i * 100] for i in range(10)])
    y_new = np.array([51000 + i * 100 for i in range(10)])
    for _ in range(150):  # Симулируем 150 сделок
        manager.retrain(X_new, y_new)
