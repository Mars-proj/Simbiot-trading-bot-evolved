from trading_bot.logging_setup import setup_logging
from trading_bot.models.local_model_api import LocalModelAPI

logger = setup_logging('online_learning')

class OnlineLearning:
    def __init__(self, market_state: dict, model_type: str = 'lstm'):
        self.volatility = market_state['volatility']
        self.model_api = LocalModelAPI(market_state, model_type)

    def update_model(self, X_new, y_new):
        """Update the model with new data."""
        try:
            # Корректируем данные на основе волатильности
            X_adjusted = X_new * (1 + self.volatility / 2)
            y_adjusted = y_new * (1 + self.volatility / 2)
            
            # Обновляем модель
            self.model_api.train(X_adjusted, y_adjusted)
            logger.info("Model updated with new data")
        except Exception as e:
            logger.error(f"Failed to update model: {str(e)}")
            raise

    def predict(self, X):
        """Make predictions using the updated model."""
        try:
            predictions = self.model_api.predict(X)
            logger.info(f"Made {len(predictions)} predictions with updated model")
            return predictions
        except Exception as e:
            logger.error(f"Failed to make predictions: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    import numpy as np
    market_state = {'volatility': 0.3}
    learner = OnlineLearning(market_state)
    X_new = np.array([[50000 + i * 100] for i in range(10)])
    y_new = np.array([51000 + i * 100 for i in range(10)])
    learner.update_model(X_new, y_new)
    predictions = learner.predict(X_new)
    print(f"Predictions: {predictions}")
